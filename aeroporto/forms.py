from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from aeroporto.table import User, users, engine, metadata
from sqlalchemy.sql import *


class RegistrationForm(FlaskForm):  
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)]) 
    email = StringField('Email',bvalidators=[DataRequired(), Email()]) 
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
    aeroportoPartenza = StringField('Aeroporto di partenza', validators=[DataRequired(), Length(min=2, max = 50)])
    aeroportoArrivo = StringField('Aeroporto di arrivo', validators=[DataRequired(), Length(min=2, max = 50)])
    submit = SubmitField('Aggiungi')