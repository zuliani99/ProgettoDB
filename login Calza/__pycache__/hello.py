# coding: utf-8
from flask import Flask, request, render_template, redirect, url_for
import sqlalchemy 
from sqlalchemy import *

from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import login_user
from flask_login import login_required
from flask_login import current_user
from flask_login import logout_user

app = Flask (__name__)

app.config['SECRET_KEY'] = 'riccardo1999'
login_manager = LoginManager()
login_manager.init_app(app)

engine = create_engine('sqlite://', echo = True) # echo = True -> dubugging (di default è false)
metadata = MetaData()

class User (UserMixin):
    # costruttore di classe
    def __init__ (self, id, email, pwd):
        self.id = id
        self.email = email
        self.pwd = pwd

users = Table ('Users', metadata, #la tabella si chiama users, e va inserita in metadeta
    Column ('id', Integer, primary_key = True), #colonne che specificanpo iol tipo e i vincoli di integrità
    Column ('email', String),
    Column ('pwd', String)
) # andiamo a memorizzare 3 componeni per ogni utente

metadata.create_all(engine) # create_all crea tutte le entità che abbiamo definito di tipo table


conn = engine.connect() # apertura di una connessione verso l ’ engine
ins = users.insert() # INSERT INTO users ( name , fullname ) VALUES (? , ?)
conn.execute (ins, [ # dati da inserire nella tabella
    {"email": "riccardo.zuliani99@gmail.com", "pwd": "vivagesu99"},
    {"email": "antonio_zuliani@alice.it", "pwd": "nonlaso1963"},
    {"email": "ginomafioso@gmail.com", "pwd": "sfacimm11"}
])
conn.close()# chiusura della connessione

@login_manager.user_loader # attenzione a questo !
def load_user(user_id):
    conn = engine.connect()
    rs = conn.execute('SELECT * FROM Users WHERE id = ? ', user_id)
    user = rs.fetchone()
    conn.close()
    return User(user.id, user.email, user.pwd)

@app.route("/")
def home():
    if current_user.is_authenticated :
        return redirect(url_for('private'))
    return render_template("base.html")


@app.route('/private')
@login_required # richiede autenticazione
def private ():
    conn = engine.connect()
    users = conn.execute('SELECT * FROM Users')
    resp = make_response(render_template("private.html", users = users ))
    conn.close()
    return resp

@app.route ('/login', methods=['GET', 'POST'])
def login ():
    if request.method == 'POST':
        conn = engine.connect()
        rs = conn.execute('SELECT pwd FROM Users WHERE email = ? ', [request.form['user']])
        real_pwd = rs.fetchone()['pwd']
        conn.close ()
        if (request.form['pass'] == real_pwd ):
            user = user_by_email(request.form['user'])
            login_user(user) # chiamata a flask - login
            return redirect(url_for('private'))
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

@app.route("/logout")
@login_required # richiede autenticazione
def logout():
    logout_user() # chiamata a flask - login
    return redirect(url_for("home"))
