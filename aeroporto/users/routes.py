from flask import render_template, url_for, flash, redirect, request, current_app, Blueprint #import necessari per il funzionamento dell'applicazione
from aeroporto import bcrypt
from aeroporto.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from flask_login import login_user, current_user, logout_user
from aeroporto.table import User, users, engine
from sqlalchemy.sql import *
from flask_principal import identity_changed, Identity, AnonymousIdentity
from datetime import datetime, date, timedelta
from aeroporto.users.utils import save_pictures, send_reset_email
from aeroporto.fly.forms import AddReviw
from aeroporto.main.utils import login_required

users = Blueprint('users', __name__)

@users.route("/register", methods=['GET', 'POST']) #metodo reguister, in cui dal file form.py inizializza un nuovo RegistrationForm(),
def register():
	if current_user.is_authenticated: 
		return redirect(url_for('main.home'))
	form = RegistrationForm()
	if form.validate_on_submit(): #controlla che tutte le regole del form siano state passate con successo
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') # criptiamo la password

		conn = engine.connect()
		#conn.execute(users.insert(),[{"username": form.username.data, "email": form.email.data, "password": hashed_password}])
		conn.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", form.username.data, form.email.data, hashed_password)
		conn.close()


		flash('Il tuo account è stato creato! Ora puoi effettuare il log in', 'success') # messaggio di avvenuto sing up al blog
		return redirect(url_for('users.login')) # redirect alla funzione home
	return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])  # metodo per la fase di login, in cui da form.py inizializza un nuovo loginform
def login():
	if current_user.is_authenticated: 
		return redirect(url_for('main.home'))
	form = LoginForm()
	if form.validate_on_submit(): #controlla che tutte le regole del form siano state passate con successo
		
		conn = engine.connect()
		#rs = conn.execute(select([users]).where(users.c.email == form.email.data))
		rs = conn.execute("SELECT * FROM users WHERE email = %s",form.email.data)
		u = rs.fetchone()
		conn.close()
		if u is not None:
			user = User(u.id, u.username, u.email, u.image_file, u.password, u.role)

			if user and bcrypt.check_password_hash(user.password, form.password.data): 
				login_user(user, remember=form.remember.data) 
				identity_changed.send(current_app._get_current_object(), identity=Identity(user.role))
				next_page = request.args.get('next') # se prima di accedere ho provato ad enbtrarte nella pagina account mi salvo i paramentri del url
				return redirect(next_page) if next_page else redirect(url_for('main.home')) # e ritorno a quella pagina altrimenti mi ritorna alla homepage
	
		flash('Login non riuscito. Controlla elìmail e password', 'danger') # messaggio di login incorretta
	return render_template('login.html', title='Login', form=form)


@users.route("/logout")
def logout(): # funzuione di logout
	logout_user()
	identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
	return redirect(url_for('main.home')) # mi riporta alla homepage

@users.route("/account", methods=['GET', 'POST'])
@login_required(role='ANY') # necessario se vogliaomo ch la pagina sia visitabile solo se l'utente ha eseguito l'accesso alla piattaforma
def account(): # funzione di account
	form = UpdateAccountForm()  # from di updaTE
	if form.validate_on_submit():  # se abbiamo cliccato aggiorna profilo
		if form.picture.data: # se abbiao aggiornato l'immagine
			picture_file = save_pictures(form.picture.data)
			current_user.image_file = picture_file
			
			conn = engine.connect()
			#conn.execute(users.update().values(image_file=current_user.image_file).where(users.c.id==current_user.id))
			conn.execute("UPDATE users SET image_file = %s WHERE id = %s", current_user.image_file, current_user.id)
			conn.close()


		current_user.username = form.username.data
		current_user.email = form.email.data
		

		conn = engine.connect()
		#u = users.update().values(username=current_user.username, email=current_user.email).where(users.c.id==current_user.id)
		#conn.execute(u)
		conn.execute("UPDATE users SET username = %s, email = %s WHERE id = %s", current_user.username, current_user.email,current_user.id)
		conn.close()

		flash('Il tuo account è stato aggionato', 'success')
		return redirect(url_for('users.account')) # non facciamo il render template, perchè altrienti il browser capirebbe che andremmo a fare un'altra post request
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	
	image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
	return render_template('account.html', title='Account', image_file=image_file, form=form) # mi porta alla pagina accout con titolo='Account'



@users.route("/user_fly", methods=['GET', 'POST'])
@login_required(role="customer")
def user_fly():
	form = AddReviw()
	conn = engine.connect()
	voli = conn.execute("SELECT p.id, p.id_volo, a1.nome, v.dataOraPartenza, a2.nome, v.dataOraArrivo, v.aereo, p.numeroPosto, v.prezzo AS pstandard,  p.prezzo_bagaglio AS pbagaglio, b.descrizione, v.prezzo+p.prezzo_bagaglio AS ptotale, p.valutazione, p.critiche FROM prenotazioni p JOIN voli v ON p.id_volo = v.id JOIN bagagli b ON p.prezzo_bagaglio=b.prezzo JOIN aeroporti a1 ON v.aeroportoPartenza=a1.id JOIN aeroporti a2 ON v.aeroportoArrivo=a2.id WHERE p.id_user= %s ORDER BY v.dataOraPartenza", current_user.id).fetchall()
	print(voli)
	conn.close()
	time = datetime.now()
	if form.is_submitted():
		print("sumbmit")
		if form.valutazione.data is not None and int(form.valutazione.data) >= 1 and int(form.valutazione.data)<= 5 and form.critiche.data is not None and form.idnascosto.data is not None:
			print("validato")
			return redirect(url_for('fly.review_fly', fly_id=form.idnascosto.data, voto=form.valutazione.data, crit=form.critiche.data))
	return render_template('imieivoli.html', voli=voli, time=time, form=form)


@users.route("/reset_password", methods=['GET', 'POST']) #route per inserire la mail per il recuper della password
@login_required()
def reset_request():
	if current_user.is_authenticated: 
		return redirect(url_for('main.home'))
	form = RequestResetForm()
	if form.validate_on_submit():

		conn = engine.connect()
		#rs = conn.execute(select([users]).where(users.c.email == form.email.data))
		rs = conn.execute("SELECT * FROM users WHERE email = %s", form.email.data)
		u = rs.fetchone()
		conn.close()
		user = User(u.id, u.nome, u.email, u.image_file, u.password, u.role)

		send_reset_email(user)  # la inviamo
		flash('Una mial ti è stata inviata con le istruzioni per resettare la password', 'info')
		return redirect(url_for('users.login'))
	return render_template('reset_request.html', title='Reset Password', form=form)

@users.route("/reset_password<token>", methods=['GET', 'POST'])
@login_required()
def reset_token(token):
	if current_user.is_authenticated: 
		return redirect(url_for('main.home'))
	user = User.verify_reset_token(token)
	if user is None: # se il token non è valido
		flash('TTOken invalido o scaduto', 'warning')
		return redirect(url_for('users.reset_request'))
	form = ResetPasswordForm() # altrimenti prendiamo la form per il reset della password
	if form.validate_on_submit(): #controlla che tutte le regole del form siano state passate con successo
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') # criptiamo la password
		user.password = hashed_password
		
		#db.session.commit() # e committiamo 
		conn = engine.connect()
		#conn.execute(users.update().values(password=user.password).where(users.c.id==user.id))
		conn.execute("UPDATE users SET password = %s WHERE id = %s", user.password, user.id)
		conn.close()

		flash('La tua password  stata aggiornata! Ora puoi eseguire il log in', 'success')
		return redirect(url_for('users.login')) # redirect alla funzione login
	return render_template('reset_token.html', title='Reset Password', form=form)
