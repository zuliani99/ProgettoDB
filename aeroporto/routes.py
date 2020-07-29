# -*- coding: utf-8 -*-
import secrets
import os
from PIL import Image #pip install Pillow
from flask import render_template, url_for, flash, redirect, request, abort #import necessari per il funzionamento dell'applicazione
from aeroporto import app, bcrypt, mail
from aeroporto.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from flask_login import login_user, current_user, logout_user, login_required
from aeroporto.table import User, datetime, users, engine, metadata, roles_required
from flask_mail import Message
from sqlalchemy.sql import *
from flask_principal import Permission, RoleNeed, ActionNeed, identity_loaded

be_admin = RoleNeed('admin')
be_customer = RoleNeed('customer')
to_sign_in = ActionNeed('sign in')

user = Permission(to_sign_in)
user.description = "User’s permissions"
admin = Permission(be_admin)
admin.description = 'Admin’s permissions'
apps_needs = [be_admin, to_sign_in]
apps_permissions = [user, admin]

@identity_loaded.connect
def on_identity_loaded(sender, identity):
    needs = []
    if identity.id in ('user', 'admin'):
        needs.append(to_sign_in)
    if identity.id == 'admin':
        needs.append(be_admin)
    
    for n in needs:
        g.identity.provides.add(n)

@app.route("/")
@app.route("/home")
def home():
    #page = request.args.get('page', 1, type=int) # richiediamo il numero di pagina nell'url, di default è 1 e deve essere un int così se ci passano cose che non sono int darà erorre
    conn = engine.connect()
    #posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5) # andiamo a prendere 5 post alla volta che sono nel database e li passiamo alla home
    #p = conn.execute(select([posts]).order_by(desc('date_posted'))).fetchall()
    #p = conn.execute(select([posts, users]).where(users.c.id == select([posts.c.user_id]).order_by(desc('date_posted')))).fetchall()
    #m = conn.execute("SELECT MAX(posts.id) FROM posts").fetchone()
    #p = conn.execute("SELECT *, ? FROM posts p JOIN users u ON p.user_id = u.id WHERE p.id BETWEEN ?+1-?-5 AND ?+1-? ORDER BY p.date_posted DESC ",page, m[0], page, m[0], page).fetchall()
    v = conn.execute("SELECT * FROM voli v JOIN aeroporti part ON v.aeropartoPartenza = part.id JOIN aeroporti arr ON v.aeropartoArrivo = arr.id JOIN aerei a ON v.aereo = a.id ORDER BY v.oraPartenza DESC ").fetchall()
    #p = conn.execute("SELECT * FROM posts ORDER BY date_posted DESC")
    #ps = p.fetchall()
    conn.close()
    #ps = Post(p.id, p.title, p.date_posted, p.content, p.user_id)
    #ps = Post(p[0], p[1], p[2], p[3], p[4])    
    return render_template('home.html', voli=v)#, page=page, mp=math.ceil(m[0]/5))

@app.route("/about") #mi renderizza il template about.html con variabuile title='About'
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST']) #metodo reguister, in cui dal file form.py inizializza un nuovo RegistrationForm(),
def register():
    if current_user.is_authenticated: 
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit(): #controlla che tutte le regole del form siano state passate con successo
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') # criptiamo la password
        #user = User(username=form.username.data, email=form.email.data, password=hashed_password) # creiamo un nuiovo user con tutti i sui attributi
        

        #db.session.add(user) # lo aggiungiamo
        #db.session.commit() # e committiamo 
        conn = engine.connect()
        conn.execute(users.insert(),[{"nome": form.nome.data, "email": form.email.data, "password": hashed_password}])
        conn.close()


        flash('Your account has been created! You are now able to log in', 'success') # messaggio di avvenuto sing up al blog
        return redirect(url_for('login')) # redirect alla funzione home
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])  # metodo per la fase di login, in cui da form.py inizializza un nuovo loginform
def login():
    if current_user.is_authenticated: 
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit(): #controlla che tutte le regole del form siano state passate con successo
        

        #user = User.query.filter_by(email=form.email.data).first() 
        conn = engine.connect()
        rs = conn.execute(select([users]).where(users.c.email == form.email.data))
        u = rs.fetchone()
        conn.close()
        if u is not None:
            user = User(u.id, u.username, u.email, u.image_file, u.password, u.role)

            if user and bcrypt.check_password_hash(user.password, form.password.data): 
                login_user(user, remember=form.remember.data) 
                identity_changed.send(current_app._get_current_object(), identity=Identity(user.role))
                next_page = request.args.get('next') # se prima di accedere ho provato ad enbtrarte nella pagina account mi salvo i paramentri del url
                return redirect(next_page) if next_page else redirect(url_for('home')) # e ritorno a quella pagina altrimenti mi ritorna alla homepage
    
        flash('Login Unsuccessful. Please check email and password', 'danger') # messaggio di login incorretta
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout(): # funzuione di logout
    logout_user()
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
    return redirect(url_for('home')) # mi riporta alla homepage

def save_pictures(form_picture): # funzione di salvataggio nel filesystem
    random_hex = secrets.token_hex(8)   #creazioen di una stringa random
    _, f_ext = os.path.splitext(form_picture.filename) # _ -> se non usaimao la variabile, ci prendiamo l'estensione del file
    picture_fn = random_hex + f_ext     #l'aggiungiamo alla stringa random
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn) # e salviamo il nuovo file nel filesystem
    
    output_size = (125, 125) # impostiamo le dimensione che vogliamo avere dell'immagine
    i = Image.open(form_picture) #apriamo l'immagine
    i.thumbnail(output_size) # cambiamo le dimensioni
    i.save(picture_path) # la risalviamo
    
    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required # necessario se vogliaomo ch la pagina sia visitabile solo se l'utente ha eseguito l'accesso alla piattaforma
def account(): # funzione di account
    form = UpdateAccountForm()  # from di updaTE
    if form.validate_on_submit():  # se abbiamo cliccato aggiorna profilo
        if form.picture.data: # se abbiao aggiornato l'immagine
            picture_file = save_pictures(form.picture.data)
            current_user.image_file = picture_file
            
            conn = engine.connect()
            conn.execute(users.update().values(image_file=current_user.image_file).where(users.c.id==current_user.id))
            conn.close()


        current_user.username = form.username.data
        current_user.email = form.email.data
        

        #db.session.commit()
        conn = engine.connect()
        u = users.update().values(username=current_user.username, email=current_user.email).where(users.c.id==current_user.id)
        conn.execute(u)
        conn.close()

        flash('Your account has been updated', 'success')
        return redirect(url_for('account')) # non facciamo il render template, perchè altrienti il browser capirebbe che andremmo a fare un'altra post request
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form) # mi porta alla pagina accout con titolo='Account'


def send_newpost_notify(title,content,aut_username,date): # funzione ch einvia una mail a tutti gli utenti con il contenuto del post
    #users = User.query.all()
    conn = engine.connect()
    user = conn.execute(select([users])).fetchall()
    conn.close()

    for usr in user:
        msg = Message('New Post By ' + aut_username, sender='noreplay@demo.com', recipients=[usr.email])
        msg.body = f'''Titolo: {title}

Data: {date}

Contenuto: {content}
'''
        mail.send(msg)





#funzione per inviare le mail
def send_reset_email(user):
    token = user.get_reset_token() #prendiamo il token
    msg = Message('Password Reset Request', sender='noreplay@demo.com', recipients=[user.email]) #header del messaggio
    msg.body = f'''To reset your password, visit the followinfg link: 
{url_for('reset_token', token=token, _external=True)}

If you did not make this request, then simply, ignore this email and no chanhìges will made
''' #body del messaggio
    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST']) #route per inserire la mail per il recuper della password
def reset_request():
    if current_user.is_authenticated: 
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        #user = User.query.filter_by(email=form.email.data).first() # prendiamo la email
        conn = engine.connect()
        rs = conn.execute(select([users]).where(users.c.email == form.email.data))
        u = rs.fetchone()
        conn.close()
        user = User(u.id, u.nome, u.email, u.image_file, u.password, u.role)

        send_reset_email(user)  # la inviamo
        flash('An email has been sent with instructions to reset you password', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated: 
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None: # se il token non è valido
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm() # altrimenti prendiamo la form per il reset della password
    if form.validate_on_submit(): #controlla che tutte le regole del form siano state passate con successo
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') # criptiamo la password
        user.password = hashed_password
        
        #db.session.commit() # e committiamo 
        conn = engine.connect()
        conn.execute(users.update().values(password=user.password).where(users.c.id==user.id))
        conn.close()

        flash('Your password has benn updated! You are now able to log in', 'success')
        return redirect(url_for('login')) # redirect alla funzione login
    return render_template('reset_token.html', title='Reset Password', form=form)


@app.route("/dashboard", methods=['GET', 'POST'])
@admin.require(http_exception=403)
def dashboard():
    return render_template('dashboard.html', title='Dashboard')