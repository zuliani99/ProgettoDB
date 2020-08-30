# -*- coding: utf-8 -*-
# Import necessari per l'applicazione
import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_mysqldb import MySQL
from flask_util_js import FlaskUtilJs

app = Flask(__name__)	# Creazione dell'applicazione Flask
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'    # Chiave necessaria per l'applicazione
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:admin@localhost/takeafly'	# Link per il database di utilizzo
bcrypt = Bcrypt(app)	# Bycrypt per il criptaggio della password
login_manager = LoginManager(app) # Creazione della variabile pe ril login dell'applicazione
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com' # Settaggio dei parametri per ila mail
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'takeaflyspa@gmail.com' # Mail che utilizzaimo per l'invio dei messaggi
app.config['MAIL_PASSWORD'] = 'Cj$Eos&dXCp3pcc#!zF!HJ7faVfSUf' # PAssword
mail = Mail(app)

fujs = FlaskUtilJs(app) # Dichiarazione della variabile per l'utilizzo della libreria FlaskUtilJs

mysql = MySQL()	# Dichiarazione della variabile per l'utilizzo di MySQL

# Configurazione del server MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = '3306'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'takeafly'
app.config['MYSQL_DATABASE_CHARSET'] = 'utf-8'

mysql.init_app(app)

# Settaggio delle variabili per l'uso di Blueprint
from aeroporto.users.routes import users
from aeroporto.fly.routes import fly
from aeroporto.main.routes import main
from aeroporto.dashboard.routes import dashboard
from aeroporto.statistics.routes import statistics
app.register_blueprint(users)
app.register_blueprint(fly)
app.register_blueprint(main)
app.register_blueprint(dashboard)
app.register_blueprint(statistics)