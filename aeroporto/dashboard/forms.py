from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DecimalField, DateField, DateTimeField, TimeField, IntegerField
from wtforms.validators import DataRequired, NumberRange, ValidationError
import datetime

#DASHBOARD
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

class FlightForm(FlaskForm):
	tomorrowDate = datetime.date.today() + datetime.timedelta(days=1)

	check = False
	aeroportoPartenza = SelectField('Aeroporto di partenza', validators=[DataRequired()])
	dataPartenza = DateField('Data partenza', default=tomorrowDate, validators=[])
	oraPartenza = TimeField('Ora partenza', validators=[])
	aeroportoArrivo = SelectField('Aeroporto di arrivo', validators=[DataRequired()])
	oraArrivo = TimeField('Ora arrivo', validators=[])
	aereo = SelectField('Aereo', validators=[DataRequired()])
	prezzo = DecimalField('Prezzo base', validators=[DataRequired()])

	#solo per l'update
	timePartenza = DateTimeField('Data e ora di partenza', validators=[])
	timeArrivo = DateTimeField('Data e ora di arrivo previste', validators=[])

	submitFlight = SubmitField()

	def validate_timeArrivo(self, timeArrivo):
		if timeArrivo.data is None and self.check: 
			raise ValidationError('This field is required')
		elif timeArrivo.data is not None and self.timePartenza.data is not None and timeArrivo.data < self.timePartenza.data:
				raise ValidationError('La data di arrivo non può essere prima della data di partenza')

	def validate_timePartenza(self, timePartenza):
		if timePartenza.data is None and self.check: 
			raise ValidationError('This field is required')	
		elif (timePartenza.data is not None and timePartenza.data.date() < self.tomorrowDate):
			raise ValidationError('La data di partenza non può essere prima di domani')

	def validate_dataPartenza(self, dataPartenza): 
		if dataPartenza.data is None and not self.check:
			raise ValidationError('This field is required')
		elif(dataPartenza.data < self.tomorrowDate):
			raise ValidationError('La data di partenza non può essere prima di domani')

	def validate_oraPartenza(self, oraPartenza):
		if(oraPartenza.data is None and not self.check):
			raise ValidationError('This field is required')
			
	def validate_oraArrivo(self, oraArrivo):
		if(oraArrivo.data is None and not self.check):
			raise ValidationError('This field is required')

	def validate_aeroportoArrivo(self, aeroportoArrivo):
		if aeroportoArrivo.data == self.aeroportoPartenza.data:
			raise ValidationError('Selezionare un aeroporto diverso da quello di partenza')

