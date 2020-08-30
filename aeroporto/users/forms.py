from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, ValidationError
from aeroporto.table import User, engine, select, users


# Form per la registrazione di un nuovo utente
class RegistrationForm(FlaskForm):  
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)]) 
	email = StringField('Email',validators=[DataRequired(), Email()]) 
	password = PasswordField('Password', validators=[DataRequired()]) 
	
	confirm_password = PasswordField('Conferma Password',
					validators=[DataRequired(), EqualTo('password')]) 

	submit = SubmitField('Registrati')

	# Validator personalizzato per verificare se l'username inserito è già in uso o meno 
	def validate_username(self, username):
		conn = engine.connect()
		u = conn.execute("SELECT * FROM users WHERE username = %s", username.data)
		user = u.fetchone()
		conn.close()
		if user: 
			raise ValidationError('Username già in uso. Scegliene uno differente.')

	# Validator personalizzato per verificare se la mail inserita è già in uso o meno 
	def validate_email(self, email):
		conn = engine.connect()
		u = conn.execute("SELECT * FROM users WHERE email = %s", email.data)
		user = u.fetchone()
		conn.close()
		if user:
			raise ValidationError('Email già in uso. Scegliene una differente.')


# Form per eseguire il login al sistema
class LoginForm(FlaskForm): 
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Ricordami')
	submit = SubmitField('Login')

# Form per eseguire il l'aggiornamneto del account
class UpdateAccountForm(FlaskForm):  
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)]) 
	email = StringField('Email', validators=[DataRequired(), Email()])
	picture = FileField('Aggiorna Foto Profilo', validators=[FileAllowed(['jpg', 'png'])]) #accetta solo file con estensione jpg e png
	submit = SubmitField('Update')

	# Validator personalizzato per verificare se l'username inserito è già in uso o meno 
	def validate_username(self, username):
		if username.data != current_user.username:
			conn = engine.connect()
			u = conn.execute("SELECT * FROM users WHERE username = %s", username.data)
			user = u.fetchone()
			conn.close()
			if user: 
				raise ValidationError('Username già in uso. Scegliene uno differente.')

	# Validator personalizzato per verificare se la mail inserita è già in uso o meno 
	def validate_email(self, email):
		if email.data != current_user.email:
			conn = engine.connect()
			u = conn.execute("SELECT * FROM users WHERE email = %s", email.data)
			user = u.fetchone()
			conn.close()
			if user:
				raise ValidationError('Email già in uso. Scegliene una differente.')

# Form per l'invio della mail per il password reset
class RequestResetForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	submit = SubmitField('Request Password Reset')

	def validate_email(self, email):
		conn = engine.connect()
		u = conn.execute("SELECT * FROM users WHERE email = %s", email.data)
		user = u.fetchone()
		conn.close()
		if user is None:
			raise ValidationError("Non c'è nessun account con quella mail. Devi prima registrarti")

# Form per il reset password
class ResetPasswordForm(FlaskForm):
	password = PasswordField('Password', validators=[DataRequired()]) 
	confirm_password = PasswordField('Conferma Password', validators=[DataRequired(), EqualTo('password')]) 
	submit = SubmitField('Reset Password')