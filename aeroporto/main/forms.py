from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField, SelectField, DateField
from wtforms.validators import DataRequired, ValidationError, Optional
import datetime

# Form per la ricerca di un volo
class SearchFlyForm(FlaskForm):
	tomorrowDate = datetime.date.today() + datetime.timedelta(days=1)
	
	aeroportoPartenza = SelectField('Aeroporto di partenza',validators=[DataRequired()])
	dataPartenza = DateField('Data partenza', default=tomorrowDate, validators=[DataRequired()])
	aeroportoArrivo = SelectField('Aeroporto di arrivo', validators=[DataRequired()])
	dataRitorno = DateField('Data ritrono', default=tomorrowDate + datetime.timedelta(days=1), validators=[DataRequired()])
	checkAndata = BooleanField('Solo Andata', default="checked", validators=[Optional()])
	checkAndataRitorno = BooleanField('Andata e Ritorno', validators=[Optional()])

	searchFly = SubmitField('Cerca Volo')

	# Creazione di validators personalizzati 
	def validate_dataPartenza(self, dataPartenza):
		if dataPartenza.data < self.tomorrowDate:
			raise ValidationError('La data deve essere futura')
	def validate_aeroportoArrivo(self, aeroportoArrivo):
		if aeroportoArrivo.data == self.aeroportoPartenza.data:
			raise ValidationError('Selezionare un aeroporto diverso da quello di partenza')
	def validate_dataRitorno(self, dataRitorno):
		if dataRitorno.data < self.dataPartenza.data:
			raise ValidationError('La data di ritrono non può essere prima di quella di partenza')