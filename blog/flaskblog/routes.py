from flask import render_template, url_for, flash, redirect, request #import necessari per il funzionamento dell'applicazione
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

posts = [       #i post che visualizzaremo all'interno
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts) #mi renderizza il template home.html con variabuile post=posts, cioè passo al home.html i due post che ho inizializzato prima


@app.route("/about") #mi renderizza il template about.html con variabuile title='About'
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST']) #metodo reguister, in cui dal file form.py inizializza un nuovo RegistrationForm(),
def register():
    if current_user.is_authenticated: # se non è autenticato lo si rinamda alla homepage
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit(): #controlla che tutte le regole del form siano state passate con successo
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') # criptiamo la password
        user = User(username=form.username.data, email=form.email.data, password=hashed_password) # creiamo un nuiovo user con tutti i sui attributi
        db.session.add(user)    # lo aggiungiamo
        db.session.commit() # e committiamo 
        flash('Your account has been created! You are now able to log in', 'success') # messaggio di avvenuto sing up al blog
        return redirect(url_for('login'))    # redirect alla funzione home
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])   # metodo per la fase di login, in cui da form.py inizializza un nuovo loginform
def login():
    if current_user.is_authenticated: # se non è autenticato lo si rinamda alla homepage
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit(): #controlla che tutte le regole del form siano state passate con successo
        user = User.query.filter_by(email=form.email.data).first() # verificaìhiamo che esista un account con quella mail
        if user and bcrypt.check_password_hash(user.password, form.password.data): # se esiste e se la decodifica della password è uguale a quella inserita
            login_user(user, remember=form.remember.data)   # uso la funzione di flask-login e gli passo a parametro l'utente e se il checkbox del ricordami password è stato riempito
            next_page = request.args.get('next')    # se prima di accedere ho provato ad enbtrarte nella pagina account mi salvo i paramentri del url
            return redirect(next_page) if next_page else redirect(url_for('home')) # e ritorno a quella pagina altrimenti mi ritorna alla homepage
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger') # messaggio di login incorretta
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout(): # funzuione di logout
    logout_user()
    return redirect(url_for('home')) # mi riporta alla homepage

@app.route("/account")
@login_required
def account():  #funzione di accoutn
    return render_template('account.html', title='Account') #mi porta alla pagina accout con titolo='Account'
 