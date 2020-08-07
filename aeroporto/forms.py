from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, DecimalField, DateField, TimeField
#from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from aeroporto.table import User, users, engine, metadata
from sqlalchemy.sql import *
import datetime

class RegistrationForm(FlaskForm):  
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)]) 
    email = StringField('Email',validators=[DataRequired(), Email()]) 
    password = PasswordField('Password', validators=[DataRequired()]) 
    
    confirm_password = PasswordField('Confirm Password',
					validators=[DataRequired(), EqualTo('password')]) 

    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        #user = User.query.filter_by(username=username.data).first()
        conn = engine.connect()
        u = conn.execute(select([users]).where(users.c.username == username.data))
        user = u.fetchone()
        conn.close()
        if user: 
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        #user = User.query.filter_by(email=email.data).first()
        conn = engine.connect()
        u = conn.execute(select([users]).where(users.c.email == email.data))
        user = u.fetchone()
        conn.close()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm): 
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):  
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)]) 
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Pictures', validators=[FileAllowed(['jpg', 'png'])]) #accetta solo file con estensione jpg e png
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            #user = User.query.filter_by(username=username.data).first() 
            conn = engine.connect()
            u = conn.execute(select([users]).where(users.c.username == username.data))
            user = u.fetchone()
            conn.close()
            if user: 
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            #user = User.query.filter_by(email=email.data).first()
            conn = engine.connect()
            u = conn.execute(select([users]).where(users.c.email == email.data))
            user = u.fetchone()
            conn.close()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')



class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        #user = User.query.filter_by(email=email.data).first()
        conn = engine.connect()
        u = conn.execute(select([users]).where(users.c.email == email.data))
        user = u.fetchone()
        conn.close()
        if user is None:
            raise ValidationError('The is no account with that email. You must register first')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()]) 
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')]) 
    submit = SubmitField('Reset Password')


class AddFlyForm(FlaskForm):
    tomorrowDate = datetime.date.today() + datetime.timedelta(days=1)
    aeroportoPartenza = SelectField('Aeroporto di partenza', default='', validators=[DataRequired()])
    dataPartenza = DateField('Data partenza', default=tomorrowDate, validators=[DataRequired()])
    oraPartenza = TimeField('Ora partenza', validators=[DataRequired()])
    aeroportoArrivo = SelectField('Aeroporto di arrivo', validators=[DataRequired()])
    oraArrivo = TimeField('Ora arrivo', validators=[DataRequired()])
    aereo = SelectField('Aereo', validators=[DataRequired()])
    prezzo = DecimalField('Prezzo base', validators=[DataRequired()])

    submit = SubmitField('Aggiungi')

    def validate_dataPartenza(self, dataPartenza):
        if dataPartenza.data < self.tomorrowDate:
            raise ValidationError('La data deve essere futura')
    def validate_aeroportoArrivo(self, aeroportoArrivo):
        if aeroportoArrivo.data == self.aeroportoPartenza.data:
            raise ValidationError('Selezionare un aeroporto diverso da quello di partenza')

class AddBooking(FlaskForm):
    bagaglio = SelectField(u'Tipo Bagaglio', choices=[('std', 'Standard - Borsa piccola'), ('pl', 'Plus - Bagaglio a mano da 10 Kg e borsa piccola'), ('del', 'Deluxe - Bagaglio a mano da 20 Kg e borsa piccola')])
    posto = SelectField(u'Posto da Sedere', coerce=int)
    submit = SubmitField('Acquista Biglietto')

class PayoutForm(FlaskForm):
    submit = SubmitField('Conferma Acquisto')