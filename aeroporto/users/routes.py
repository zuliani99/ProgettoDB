from flask import render_template, url_for, flash, redirect, request, current_app, Blueprint, abort #import necessari per il funzionamento dell'applicazione
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

# Utilizzo di Blueprint per mappare il progetto in gruppi di funzionalità
users = Blueprint('users', __name__)

# Route per la registrazione di un nuovo utente
@users.route("/register", methods=['GET', 'POST']) 
def register():
	if current_user.is_authenticated: 	# Se l'utente è già autenticato lo rindiriziamo alla home
		return redirect(url_for('main.home'))
	form = RegistrationForm()
	if form.validate_on_submit(): # Controlla che tutte le regole di validazione del form siano state superate con successo
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') # Criptiamo la password

		conn = engine.connect()
		# Inseriamo il nuovo utente nel database
		conn.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", form.username.data, form.email.data, hashed_password)
		conn.close()

		flash('Il tuo account è stato creato! Ora puoi effettuare il log in', 'success')
		return redirect(url_for('users.login'))
	return render_template('register.html', title='Register', form=form)

# Route per l'accesso al sistema
@users.route("/login", methods=['GET', 'POST']) 
def login():
	if current_user.is_authenticated:  # Se l'utente è già autenticato lo rindiriziamo alla home
		return redirect(url_for('main.home'))
	form = LoginForm()
	if form.validate_on_submit(): # Controlla che tutte le regole di validazione del form siano state superate con successo
		conn = engine.connect()
		rs = conn.execute("SELECT * FROM users WHERE email = %s",form.email.data) # Restituiamo l'utente che ha come email quella che abbiamo inserito nel form
		u = rs.fetchone()
		conn.close()
		if u is not None: # Se il risultato della query è diverso da None
			user = User(u.id, u.username, u.email, u.image_file, u.password, u.role)	# Creiamo l'oggetto utente
			if user and bcrypt.check_password_hash(user.password, form.password.data): # Se le due passowrd coincidono l'utente può accedere al sistema con il suo account
				login_user(user, remember=form.remember.data) 
				identity_changed.send(current_app._get_current_object(), identity=Identity(user.role)) # Cambiamo l'identità di chi ha fatto l'accesso
				return redirect(url_for('main.home')) 

		flash('Login non riuscito. Controlla elìmail e password', 'danger')
	return render_template('login.html', title='Login', form=form)


# Route per il logout
@users.route("/logout")
def logout(): 
	logout_user()
	identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
	return redirect(url_for('main.home'))


# Route per visualizzare e modificare i parametri del proprio'account
@users.route("/account", methods=['GET', 'POST'])
@login_required(role='ANY') # Paginqa accessibile sia a customer che a admin
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data: # Se abbiao aggiornato l'immagine
			picture_file = save_pictures(form.picture.data) # Richiamiamo la funzione save_picture per il salvataggio dell'immagine
			current_user.image_file = picture_file	#L'aggiorniamo
			
			conn = engine.connect() # E l'aggiorniamo nel database
			conn.execute("UPDATE users SET image_file = %s WHERE id = %s", current_user.image_file, current_user.id)
			conn.close()


		current_user.username = form.username.data
		current_user.email = form.email.data
		

		conn = engine.connect()		# Aggiorniamo username e/o email con i parametri inseriti a form
		conn.execute("UPDATE users SET username = %s, email = %s WHERE id = %s", current_user.username, current_user.email,current_user.id)
		conn.close()

		flash('Il tuo account è stato aggionato', 'success')
		return redirect(url_for('users.account'))
	elif request.method == 'GET':	# Se la richiesta è una get impostiamo i valori del form ai parametri attuali del account
		form.username.data = current_user.username
		form.email.data = current_user.email
	
	image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
	return render_template('account.html', title='Account', image_file=image_file, form=form)


# Route per visualizzare i proprio voli prenotati
@users.route("/user_fly", methods=['GET', 'POST'])
@login_required(role="customer")	# Route accessibile solo ai clienti
def user_fly():
	form = AddReviw()
	conn = engine.connect()	# Restituiamo le principali informazioni delle prenotazioni del utente 
	voli = conn.execute(
		"SELECT p.id, p.id_volo, a1.nome, v.dataOraPartenza, a2.nome, v.dataOraArrivo, v.aereo, p.numeroPosto, b.descrizione, p.prezzotot, p.valutazione, p.critiche " +
		"FROM prenotazioni p JOIN voli v ON p.id_volo = v.id JOIN bagagli b ON p.prezzo_bagaglio=b.prezzo JOIN aeroporti a1 ON v.aeroportoPartenza=a1.id JOIN aeroporti a2 ON v.aeroportoArrivo=a2.id "+
		"WHERE p.id_user= %s ORDER BY v.dataOraPartenza", current_user.id
	).fetchall()
	conn.close()
	time = datetime.now() # Ci salviamo la data e ora attiuale in una variabile che poi passeremo nella pagina html
	if form.is_submitted():
		if form.valutazione.data is not None and int(form.valutazione.data) >= 1 and int(form.valutazione.data)<= 5 and form.critiche.data is not None and form.idnascosto.data is not None:
			# Se si è inserita una recensione al volo passiamo la valutazione con le critiche a review_fly
			return redirect(url_for('fly.review_fly', fly_id=form.idnascosto.data, voto=form.valutazione.data, crit=form.critiche.data))
	return render_template('imieivoli.html', voli=voli, time=time, form=form)


# Route per l'inserimento della mail per il password reset
@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated: # Se l'utente ha già eseguito l'accesso lo rindirizziamo alla home
		return redirect(url_for('main.home'))
	form = RequestResetForm()
	if form.validate_on_submit():
		conn = engine.connect() # Restituiamo l'utente che ha come email quella che abbiamo inserito nel form
		rs = conn.execute("SELECT * FROM users WHERE email = %s", form.email.data)
		u = rs.fetchone()
		conn.close()	
		user = User(u.id, u.username, u.email, u.image_file, u.password, u.role)	# Creiamo l'oggetto utente con i sui parametri

		send_reset_email(user)  # Richiamiamo la funzione send_reset_email per l'invio della mial al utente
		flash('Una mail ti è stata inviata con le istruzioni per resettare la password', 'info')
		return redirect(url_for('users.login'))
	return render_template('reset_request.html', title='Reset Password', form=form)


# Route per l'inserimento della nuova passowrd
@users.route("/reset_password<token>", methods=['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated: # Se l'utente ha già eseguito l'accesso lo rindirizziamo alla home
		return redirect(url_for('main.home'))
	user = User.verify_reset_token(token)	# Richiamiamo la funzione verify_reset_token per verificare il token attuale se sia valido o meno
	if user is None:
		flash('Tosken invalido o scaduto', 'warning')
		return redirect(url_for('users.reset_request'))
	form = ResetPasswordForm() 
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') # Criptiamo la password
		user.password = hashed_password	# Aggiorniamo la passowrd del utente
		
		conn = engine.connect()	 # Aggiorniamo la password nel database
		conn.execute("UPDATE users SET password = %s WHERE id = %s", user.password, user.id)
		conn.close()

		flash('La tua password  stata aggiornata! Ora puoi eseguire il log in', 'success')
		return redirect(url_for('users.login'))
	return render_template('reset_token.html', title='Reset Password', form=form)


# Route per l'eliminazione del priprio account
@users.route("/delete_account<int:id_account>", methods=['POST'])
@login_required(role="customer") # Funzione disponibile solamente per i clienti
def delete_account(id_account):
	if id_account != current_user.id:	# Se l'utente che ha richiesto l'eliminazione di un accaout non è lui stesso si abortisce
		return redirect(url_for("main.home"))
	else:
		conn = engine.connect()	# Altrimenti eseguiamo la rimozione effettiva dell'account del database
		conn.execute("DELETE FROM users WHERE id = %s", id_account)
		conn.close()
		flash("Account eliminato con successo", 'success')
		return redirect(url_for('users.logout'))