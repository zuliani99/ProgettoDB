from flask_wtf import FlaskForm
from wtforms import DateField, SubmitField
from wtforms.validators import ValidationError, Optional
import datetime

class StatisticsForm(FlaskForm):
	dataA = DateField("Data inizio", validators=[Optional()])
	dataB = DateField("Data fine", validators=[Optional()])

	submitFilter = SubmitField("Cerca per data/e")

	def validate_dataB(self, dataB):
		if self.dataA.data is not None and dataB.data is not None and self.dataA.data > dataB.data:
			raise ValidationError('La data di arrivo non può essere prima della data di partenza')
	