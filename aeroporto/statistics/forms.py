from flask_wtf import FlaskForm
from wtforms import DateField, SubmitField
from wtforms.validators import ValidationError
import datetime

class StatisticsForm(FlaskForm):
	dataA = DateField("Data inizio", validators=[])
	dataB = DateField("Data fine", validators=[])

	submitFilter= SubmitField()

	def validate_dataB(self, dataB):
		if self.dataA.data > dataB.data:
				raise ValidationError('La data di arrivo non può essere prima della data di partenza')
	