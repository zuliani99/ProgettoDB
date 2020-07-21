from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField # import per tipologia dei dati che andremo ad inserire nel form
from wtforms.validators import DataRequired, Length, Email, EqualTo # import per la verifica dei dati inseriti nei form


class RegistrationForm(FlaskForm):      #classe per il form di registrazione
    username = StringField('Username',  #l'username è di tipo stringfield e a livello client sarà chiamamto 'Username' e avrà le sueguenti regole per essere valido DataRequired(), Length(min=2, max=20)
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',    #la mail è di tipo stringfield e a livello client si chiamerà 'Email' e avrà come regole DataRequired(), Email()
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])   # la password è di tipo passwordfield e sarà visualizzata a livello client come 'Password'
                                                                        # come regole avrà DataRequired()
    confirm_password = PasswordField('Confirm Password',        # confirm_password è di tipo passwordfield e sarò visualizzata a livello client come 'Confirm Password'
                                                                # come regole avrà DataRequired(), EqualTo('password')
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm): #classe per il form di login, stessi commenti della registrationform
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
