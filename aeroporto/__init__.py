# -*- coding: utf-8 -*-
import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'    #chiave necessaria per l'applicazione
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin@localhost/MyDB'
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'noreplayblogprova@gmail.com' # mail che utilizzaimo per l'invio dei messaggi
app.config['MAIL_PASSWORD'] = 'blogprova4852' # questa è la password
mail = Mail(app)

mysql = MySQL()

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'MyDB'

mysql.init_app(app)

from aeroporto import routes


