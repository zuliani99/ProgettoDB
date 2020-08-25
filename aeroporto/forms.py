from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, DecimalField, DateField, DateTimeField,TimeField, IntegerField, BooleanField
#from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, ValidationError, Optional
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



class AddBookingGone(FlaskForm):
    bagaglioAndata = SelectField(u'Tipo Bagaglio')
    postoAndata = StringField('Posto da Sedere', validators=[DataRequired()])
    submit = SubmitField('Conferma Aquisto')


class AddReviw(FlaskForm):
    valutazione = SelectField(u'Valutazione Volo', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    critiche = TextAreaField('Critica', validators=[Length(max=200),DataRequired()])
    idnascosto = StringField('Id nascosto', validators=[DataRequired()])  
    submit = SubmitField('Inserisci')


#DASHBOARD
class AddFlyForm(FlaskForm):
    tomorrowDate = datetime.date.today() + datetime.timedelta(days=1)

    aeroportoPartenza = SelectField('Aeroporto di partenza', validators=[DataRequired()])
    dataPartenza = DateField('Data partenza', default=tomorrowDate, validators=[DataRequired()])
    oraPartenza = TimeField('Ora partenza', validators=[DataRequired()])
    aeroportoArrivo = SelectField('Aeroporto di arrivo', validators=[DataRequired()])
    oraArrivo = TimeField('Ora arrivo', validators=[DataRequired()])
    aereo = SelectField('Aereo', validators=[DataRequired()])
    prezzo = DecimalField('Prezzo base', validators=[DataRequired()])

    submitFly = SubmitField()

    def validate_dataPartenza(self, dataPartenza):
        if dataPartenza.data < self.tomorrowDate:
            raise ValidationError('La data deve essere futura')
    def validate_aeroportoArrivo(self, aeroportoArrivo):
        if aeroportoArrivo.data == self.aeroportoPartenza.data:
            raise ValidationError('Selezionare un aeroporto diverso da quello di partenza')

class PlaneForm(FlaskForm):
    nome = StringField('Nome aereo', validators=[DataRequired()])
    nPosti = IntegerField('Numero di posti', validators=[DataRequired(), NumberRange(1, None,"L'aereo deve avere almeno quattro posti ")])

    submitPlane = SubmitField()

    def validate_nPosti(self, nPosti):
        if nPosti.data % 4 != 0:
            raise ValidationError('Il numero dei posti deve essere divisibile per quattro')

class AirportForm(FlaskForm):
    nome = StringField('Nome aeroporto', validators=[DataRequired()])
    indirizzo = StringField('Indirizzo',validators=[DataRequired()])

    submitAirport= SubmitField()


#NON SERVE FORSE, PROVO AD USARE L'ALTRO FORM
class UpdateFlyForm(FlaskForm):
    tomorrowDate = datetime.date.today() + datetime.timedelta(days=1)
    
    aeroportoPartenza = SelectField('Aeroporto di partenza', default='', validators=[DataRequired()])
    timePartenza = DateTimeField('Data e ora di partenza', validators=[DataRequired()])
    aeroportoArrivo = SelectField('Aeroporto di arrivo', validators=[DataRequired()])
    timeArrivo = DateTimeField('Data e ora di arrivo previste', validators=[DataRequired()])
    aereo = SelectField('Aereo', validators=[DataRequired()])
    prezzo = DecimalField('Prezzo base', validators=[DataRequired()])

    updateFly = SubmitField()

    def validate_dataPartenza(self, dataPartenza):
        if dataPartenza.data < self.tomorrowDate:
            raise ValidationError('La data deve essere futura')
    def validate_aeroportoArrivo(self, aeroportoArrivo):
        if aeroportoArrivo.data == self.aeroportoPartenza.data:
            raise ValidationError('Selezionare un aeroporto diverso da quello di partenza')

class SearchFlyForm(FlaskForm):
    tomorrowDate = datetime.date.today() + datetime.timedelta(days=1)
    
    aeroportoPartenza = SelectField('Aeroporto di partenza',validators=[DataRequired()])
    dataPartenza = DateField('Data partenza', default=tomorrowDate, validators=[DataRequired()])
    aeroportoArrivo = SelectField('Aeroporto di arrivo', validators=[DataRequired()])
    dataRitorno = DateField('Data ritrono', validators=[Optional()])
    checkAndata = BooleanField('Solo Andata', default="checked", validators=[Optional()])
    checkAndataRitorno = BooleanField('Andata e Ritorno', validators=[Optional()])

    searchFly = SubmitField('Cerca Volo')
    #buyStep = SubmitField('Continua')

    def validate_dataPartenza(self, dataPartenza):
        if dataPartenza.data < self.tomorrowDate:
            raise ValidationError('La data deve essere futura')
    def validate_aeroportoArrivo(self, aeroportoArrivo):
        if aeroportoArrivo.data == self.aeroportoPartenza.data:
            raise ValidationError('Selezionare un aeroporto diverso da quello di partenza')
    def validate_daraRitorno(self, dataRitorno):
        if dataRitorno < self.dataPartenza.data:
            raise ValidationError('La data di ritrono non può essere prima di quella di partenza')
        if dataRitorno is None and self.cheackAndataRitorno.data == False:
            raise ValidationError('Scegliere una data di ritorno')


class AddBookingReturn(FlaskForm):
    bagaglioAndata = SelectField(u'Tipo Bagaglio')
    postoAndata = StringField('Posto da Sedere', validators=[DataRequired()])
    bagaglioRitorno = SelectField(u'Tipo Bagaglio')
    postoRitorno = StringField('Posto da Sedere', validators=[DataRequired()])
    submit = SubmitField('Conferma Aquisto')