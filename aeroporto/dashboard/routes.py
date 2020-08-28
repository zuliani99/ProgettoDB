from flask import render_template, url_for, flash, redirect, request, Blueprint#import necessari per il funzionamento dell'applicazione
from aeroporto.dashboard.forms import PlaneForm, AirportForm, FlightForm
from aeroporto.table import engine, voli, aerei, aeroporti, deleteElementByID
from sqlalchemy.sql import *
from datetime import datetime, timedelta
from aeroporto.main.utils import login_required

dashboard = Blueprint('dashboard', __name__)

@dashboard.route("/delete_volo<int:volo_id>", methods=['GET', 'POST'])
@login_required(role="admin")
def delete_volo(volo_id):

	result = deleteElementByID("id", volo_id, "voli")
	if result:
		flash('Il volo ' + str(volo_id) + ' è stato cancellato con successo', 'success')

	return redirect(url_for('dashboard.dashboard'))

@dashboard.route("/delete_aeroporto<int:aeroporto_id>", methods=['GET', 'POST'])
@login_required(role="admin")

def delete_aeroporto(aeroporto_id):
	
	result = deleteElementByID("id", aeroporto_id, "aeroporti")
	if result:
		flash('l\'aeroporto ' + str(aeroporto_id) + ' è stato cancellato con successo', 'success')
		
	return redirect(url_for('dashboard.dashboard'))

@dashboard.route("/delete_aereo<int:aereo_id>", methods=['GET','POST'])
@login_required(role="admin")
def delete_aereo(aereo_id):

	result = deleteElementByID("id", aereo_id, "aerei")
	if result:
		flash('l \'aereo ' + str(aereo_id) + ' è stato cancellato con successo', 'success')
	
	return redirect(url_for('dashboard.dashboard'))

@dashboard.route("/dashboardhome", methods=['GET', 'POST'])
@login_required(role="admin")
def dashboardhome():
	flightForm = FlightForm()
	planeForm = PlaneForm()
	airportForm = AirportForm()

	conn = engine.connect()
	aeroporti = conn.execute("SELECT id, nome, indirizzo FROM aeroporti").fetchall()
	aerei = conn.execute("SELECT id, nome, numeroPosti FROM aerei").fetchall()
	voli = conn.execute("SELECT * FROM voli JOIN pren_volo ON pren_volo.id = voli.id").fetchall()
	conn.close()

	opzioniAeroporti = [(str(choice[0]), str(choice[1]+", "+choice[2]+" #"+str(choice[0]))) for choice in aeroporti]
	flightForm.aeroportoPartenza.choices = [('','')] + opzioniAeroporti
	flightForm.aeroportoArrivo.choices = [('','')] + opzioniAeroporti

	opzioniAerei = [(str(choice[0]), str(choice[1]+" #"+str(choice[0]))) for choice in aerei]
	flightForm.aereo.choices = [('','')]  + opzioniAerei
	
	time = datetime.now()

	flightForm.check = False;

	if flightForm.is_submitted() and flightForm.submitFlight.data:
		if flightForm.validate():
			oraPartenza = datetime.combine(flightForm.dataPartenza.data, flightForm.oraPartenza.data)
			if flightForm.oraPartenza.data > flightForm.oraArrivo.data:
				oraArrivo = datetime.combine(flightForm.dataPartenza.data + timedelta(days=1), flightForm.oraArrivo.data)
			else:
				oraArrivo = datetime.combine(flightForm.dataPartenza.data, flightForm.oraArrivo.data)

			conn = engine.connect()
			#conn.execute(voli.insert(),[{"aeroportoPartenza": flightForm.aeroportoPartenza.data,"oraPartenza": oraPartenza,"aeroportoArrivo": flightForm.aeroportoArrivo.data,"oraArrivo": oraArrivo,"aereo": flightForm.aereo.data,"prezzo": flightForm.prezzo.data}])
			conn.execute("INSERT INTO voli (aeroportoPartenza, dataOraPartenza, aeroportoArrivo, dataOraArrivo, aereo,prezzo) VALUES (%s,%s,%s,%s,%s,%s)", 
				flightForm.aeroportoPartenza.data, 
				oraPartenza, 
				flightForm.aeroportoArrivo.data, 
				oraArrivo, 
				flightForm.aereo.data,
				flightForm.prezzo.data
			)
			conn.close()
		   
			flash('Aggiunta volo completata con successo :D', 'success')
			return redirect('dashboard')
		else:
			flash('Qualcosa nell\'inserimento del volo è andato storto :(', 'danger')
	
	if planeForm.is_submitted() and planeForm.submitPlane.data:
		if planeForm.validate():
			conn = engine.connect()
			conn.execute("INSERT INTO aerei (nome, numeroPosti) VALUES (%s, %s)", planeForm.nome.data, planeForm.nPosti.data)

			#se si usa questa linea: typeerror insert() takes exactly 2 arguments (0 given) python mysql
			#conn.execute(aerei.insert(),[{"name": planeForm.nome.data, "numeroPosti": planeForm.nPosti.data}])

			conn.close()

			flash('Aggiunta aereo completata con successo :)', 'success')
			return redirect('dashboard')
		else:
			flash('Qualcosa nell\'inserimento dell\'aereo è andato storto :(', 'danger')
	
	if airportForm.is_submitted() and airportForm.submitAirport.data:
		if airportForm.validate():
			conn = engine.connect()
			conn.execute("INSERT INTO aeroporti (nome, indirizzo) VALUES (%s, %s)", airportForm.nome.data, airportForm.indirizzo.data)

			#conn.execute(aeroporti.insert(),[{"name": airportForm.nome.data, "indirizzo": airportForm.indirizzo.data}])
			conn.close()

			flash('Aggiunta aeroporto completata con successo :D', 'success')
			return redirect('dashboard')
		else:
			flash('Qualcosa nell\'inserimento dell\'aeroporto è andato storto :(', 'danger')

	return render_template('dashboard.html', title='Dashboard', flightForm=flightForm, planeForm=planeForm, airportForm=airportForm, voli=voli, aeroporti=aeroporti, aerei=aerei,time=time)



@dashboard.route("/dashboard_volo<volo_id>", methods=['GET', 'POST'])
@login_required(role="admin") 
def configVolo(volo_id): 
	updateForm = FlightForm() 

	conn = engine.connect()
	volo = conn.execute("SELECT id, aeroportoPartenza, dataOraPartenza, aeroportoArrivo, dataOraArrivo, aereo, prezzo FROM voli WHERE id=%s", volo_id).fetchone()
	aeroporti = conn.execute("SELECT id, nome, indirizzo FROM aeroporti").fetchall()
	aerei = conn.execute("SELECT id, nome FROM aerei").fetchall()
	voli = conn.execute("SELECT * FROM voli").fetchall()
	conn.close()

	opzioniAeroporti = [(str(choice[0]), str(choice[1]+", "+choice[2]+" #"+str(choice[0]))) for choice in aeroporti]
	updateForm.aeroportoPartenza.choices = [('','')] + opzioniAeroporti
	updateForm.aeroportoArrivo.choices = [('','')] + opzioniAeroporti


	opzioniAerei = [(str(choice[0]), str(choice[1]+" #"+str(choice[0]))) for choice in aerei]
	updateForm.aereo.choices = [('','')]  + opzioniAerei

	#Set the informations of the fly in each field 
	if updateForm.validate_on_submit():
		conn = engine.connect()
		
		conn.execute("UPDATE voli SET aeroportoPartenza=%s, dataOraPartenza=%s,aeroportoArrivo=%s,dataOraArrivo=%s,aereo=%s,prezzo=%s WHERE id = %s", 
			updateForm.aeroportoPartenza.data,
			updateForm.timePartenza.data,
			updateForm.aeroportoArrivo.data,
			updateForm.timeArrivo.data,
			updateForm.aereo.data,
			updateForm.prezzo.data,
			volo_id
		)
		conn.close()
		flash('Aggiornamento volo completato con successo :D', 'success')
		return redirect('dashboard')
	elif request.method == 'GET':
		updateForm.aeroportoPartenza.data = str(volo[1])
		updateForm.timePartenza.data = volo[2]
		updateForm.aeroportoArrivo.data = str(volo[3])
		updateForm.timeArrivo.data = volo[4]
		updateForm.aereo.data = str(volo[5])
		updateForm.prezzo.data = volo[6]
		
	return render_template('dashboard_volo.html', volo=volo, flightForm=updateForm)

@dashboard.route("/dashboard_aeroporto<aeroporto_id>", methods=['GET', 'POST'])
@login_required(role="admin")
def configAeroporto(aeroporto_id):
	updateform = AirportForm()

	conn = engine.connect()
	aeroporto = conn.execute("SELECT id, nome, indirizzo FROM aeroporti WHERE id = %s", aeroporto_id).fetchone()
	conn.close()

	if updateform.validate_on_submit():
		conn = engine.connect()
		conn.execute("UPDATE aeroporti SET nome=%s, indirizzo=%s WHERE id = %s",
			updateform.nome.data,
			updateform.indirizzo.data,
			aeroporto_id
		)
		conn.close()
		flash('Aggiornamento aeroporto completato con successo :D', 'success')
		return redirect('dashboard')
	elif request.method == 'GET':
		updateform.nome.data = aeroporto[1]
		updateform.indirizzo.data = aeroporto[2]
		#updateform.submitAirport.label = "Aggiorna"

	return render_template('dashboard_aeroporto.html', aeroporto=aeroporto, airportForm=updateform)

@dashboard.route("/dashboard_aereo<aereo_id>", methods=['GET', 'POST'])
@login_required(role="admin")
def configAereo(aereo_id):
	updateform = PlaneForm()

	conn = engine.connect()
	aereo = conn.execute("SELECT id, nome, numeroPosti FROM aerei WHERE id = %s", aereo_id).fetchone()
	conn.close()

	if updateform.validate_on_submit():
		conn = engine.connect()
		conn.execute("UPDATE aerei SET nome=%s, numeroPosti=%s WHERE id = %s",
			updateform.nome.data,
			updateform.nPosti.data,
			aereo_id
		)
		conn.close()
		flash('Aggiornamento aereo completato con successo :D', 'success')
		return redirect('dashboard')
	elif request.method == 'GET':
		updateform.nome.data = aereo[1]
		updateform.nPosti.data = aereo[2]
		#updateform.submitAirport.label = "Aggiorna"

	return render_template('dashboard_aereo.html', aereo=aereo, planeForm=updateform)