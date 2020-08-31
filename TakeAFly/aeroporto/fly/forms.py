from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Optional

# Form per volo di sola andata
class AddBookingGone(FlaskForm): 
	bagaglioAndata = SelectField(u'Tipo Bagaglio')
	postoAndata = StringField('Posto da Sedere', validators=[DataRequired()])
	submit = SubmitField('Conferma Aquisto')


class AddReviw(FlaskForm): 	# Form per aggiungere la recensione al volo
	valutazione = SelectField(u'Valutazione Volo', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
	critiche = TextAreaField('Critica', validators=[DataRequired()])
	idnascosto = StringField('Id nascosto', validators=[DataRequired()])  
	submit = SubmitField('Inserisci')	


class AddBookingReturn(FlaskForm): # Form per volo di andata e ritorno
	bagaglioAndata = SelectField(u'Tipo Bagaglio')
	postoAndata = StringField('Posto da Sedere', validators=[DataRequired()])
	bagaglioRitorno = SelectField(u'Tipo Bagaglio')
	postoRitorno = StringField('Posto da Sedere', validators=[DataRequired()])
	submit = SubmitField('Conferma Aquisto')
