from flask import Blueprint, render_template, request
from sqlalchemy.sql import *
from aeroporto.table import engine
from datetime import datetime
from aeroporto.main.forms import SearchFlyForm


# Utilizzo di Blueprint per mappare il progetto in gruppi di funzionalità
main = Blueprint('main', __name__)

# Route per la HomePage dell'applicazione
@main.route("/", methods=['GET', 'POST'])
@main.route("/home", methods=['GET', 'POST'])
def home():
	searchForm = SearchFlyForm() # Richiamo il from

	andata=ritorno=[]	# Istanzio andata e ritorno a liste vuote
	is_return = False 	# Istanzio il booleno per veriicare se il volo che volgio cercare sia di solo andata oppure di andata e ritorno

	conn = engine.connect() # Istanzio una connessione
	aeroporti = conn.execute("SELECT id, nome, indirizzo FROM aeroporti").fetchall() # Restituisco tutti gli aeroporti
	
	# Inserirsco nel SelectField gli aeroporti disponibili
	opzioniAeroporti = [(str(choice[0]), str(choice[1]+", "+choice[2])) for choice in aeroporti]
	searchForm.aeroportoPartenza.choices = [('','')] + opzioniAeroporti
	searchForm.aeroportoArrivo.choices = [('','')] + opzioniAeroporti

	if searchForm.validate_on_submit():
		print("ok")
		# Salvatagglio dei valori inseritinel form su variabili
		aPart = searchForm.aeroportoPartenza.data
		aArr = searchForm.aeroportoArrivo.data
		dPart = searchForm.dataPartenza.data
		dRit = searchForm.dataRitorno.data
		is_return = searchForm.checkAndataRitorno.data

		#print(str(aPart) + " " + str(dPart)  + " " + str(aArr) + " " + str(dRit) + " " + str(is_return))
		#queryandata = "SELECT v.id , part.nome, v.dataOraPartenza, arr.nome, v.dataOraArrivo, v.prezzo FROM voli v, aeroporti arr, aeroporti part, aerei a 
		#WHERE v.aeroportoArrivo = arr.id AND v.aeroportoPartenza = part.id AND v.aereo = a.id AND part.id = "+str(aPart)+" AND arr.id = "+str(aArr)+" AND v.dataOraPartenza BETWEEN '"+str(dPart)+" 00:00:00' AND '"+str(dPart)+" 23:59:59'"
		#print(query)

		# Resrituisco le informazioni del volo di andata filtrate per i campi del form
		'''print("SELECT v.id , part.nome, v.dataOraPartenza, arr.nome, v.dataOraArrivo, v.prezzo " +
			"FROM voli v, aeroporti arr, aeroporti part, aerei a WHERE v.aeroportoArrivo = arr.id AND v.aeroportoPartenza = part.id AND v.aereo = a.id AND part.id = "+aPart+" AND arr.id = "+aArr+" AND v.dataOraPartenza BETWEEN "
			+(dPart.strftime("%Y-%m-%d") + " 00:00:00")+" AND "+(dPart.strftime("%Y-%m -%d") + " 23:59:59"))'''
		andata = conn.execute(
			"SELECT v.id , part.nome, v.dataOraPartenza, arr.nome, v.dataOraArrivo, v.prezzo " +
			"FROM voli v, aeroporti arr, aeroporti part, aerei a WHERE v.aeroportoArrivo = arr.id AND v.aeroportoPartenza = part.id AND v.aereo = a.id AND part.id = %s AND arr.id = %s AND v.dataOraPartenza BETWEEN %s AND %s",
			aPart, aArr, (dPart.strftime("%Y-%m-%d") + " 00:00:00"), (dPart.strftime("%Y-%m-%d") + " 23:59:59")
		).fetchall()

		if dRit is not None:
			#queryritorno = "SELECT v.id , part.nome, v.dataOraPartenza, arr.nome, v.dataOraArrivo, v.prezzo FROM voli v, aeroporti arr, aeroporti part, aerei a WHERE v.aeroportoArrivo = arr.id AND v.aeroportoPartenza = part.id AND v.aereo = a.id AND part.id = "+str(aArr)+" AND arr.id = "+str(aPart)+" AND v.dataOraPartenza BETWEEN '"+str(dRit)+" 00:00:00' AND '"+str(dRit)+" 23:59:59'"
			# Resrituisco le informazioni del volo di ritorno filtrate per i campi del form
			ritorno = conn.execute(
				"SELECT v.id , part.nome, v.dataOraPartenza, arr.nome, v.dataOraArrivo, v.prezzo " + 
				"FROM voli v, aeroporti arr, aeroporti part, aerei a WHERE v.aeroportoArrivo = arr.id AND v.aeroportoPartenza = part.id AND v.aereo = a.id AND part.id = %s AND arr.id = %s AND v.dataOraPartenza BETWEEN %s AND %s",
				aArr, aPart, (dRit.strftime("%Y-%m-%d") + " 00:00:00"), (dRit.strftime("%Y-%m-%d") + " 23:59:59")
			).fetchall()


	else:
		# Resrituisco le informazioni del volo di andata filtrate per i campi del form
		andata = conn.execute(
			"SELECT v.id , part.nome, v.dataOraPartenza, arr.nome, v.dataOraArrivo, v.prezzo " + 
			"FROM voli v, aeroporti arr, aeroporti part, aerei a WHERE v.aeroportoArrivo = arr.id and v.aeroportoPartenza = part.id and v.aereo = a.id and v.dataOraPartenza > %s ORDER BY v.dataOraPartenza ASC", datetime.utcnow()).fetchall()
		
	conn.close()
	return render_template('home.html', voliand=andata, volirit=ritorno, flyForm=searchForm, is_return=is_return)
