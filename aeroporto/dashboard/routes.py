#import necessari per il funzionamento dell'applicazione
from flask import render_template, url_for, flash, redirect, request, Blueprint
from aeroporto.dashboard.forms import PlaneForm, AirportForm, FlightForm
from aeroporto.table import engine, voli, aerei, aeroporti, deleteElementByID
from sqlalchemy.sql import *
from datetime import datetime, timedelta
from aeroporto.main.utils import login_required
from aeroporto.dashboard.utils import send_mail_deletefly


dashboard = Blueprint('dashboard', __name__)

@dashboard.route("/delete_volo<int:volo_id>", methods=['GET', 'POST'])
@login_required(role="admin")
def delete_volo(volo_id):

	conn = engine.connect()
	#Legge le prenotazioni collegate a quel volo
	usersmail = conn.execute("SELECT u.email FROM users u JOIN prenotazioni p on u.id = p.id_user WHERE p.id_volo = %s", volo_id).fetchall()

	#Crea l'array
	listmail = []
	for mail in usersmail:
		listmail.append(mail[0])

	trans = conn.begin() 	#Inizia la transazione

	try:
		result = deleteElementByID("id", volo_id, "voli") 		#Elimina il volo

		if result:												
			if not listmail == []:								
				send_mail_deletefly(volo_id, listmail)			#Invia la mail di avviso ai clienti 
			trans.commit()										#Esegue la commit confermando le azioni all'interno della transazione
			flash('Il volo ' + str(volo_id) + ' è stato cancellato con successo', 'success')
	except:
		trans.rollback()	
		raise									#Se qualcosa è andato storto la rollback ripristina lo stato precedente della tabella
		flash('Il volo NON ' + str(volo_id) + ' è stato cancellato', 'danger')
	finally:
		conn.close()											#In qualunque caso chiude la connessione
	return redirect(url_for('dashboard.dashboardhome'))			#Ritorna alla pagina principale della dashboard

@dashboard.route("/delete_aeroporto<int:aeroporto_id>", methods=['GET', 'POST'])
@login_required(role="admin")

def delete_aeroporto(aeroporto_id):
	
	result = deleteElementByID("id", aeroporto_id, "aeroporti")
	if result:
		flash('l\'aeroporto ' + str(aeroporto_id) + ' è stato cancellato con successo', 'success')
		
	return redirect(url_for('dashboard.dashboardhome'))

@dashboard.route("/delete_aereo<int:aereo_id>", methods=['GET','POST'])
@login_required(role="admin")
def delete_aereo(aereo_id):

	result = deleteElementByID("id", aereo_id, "aerei")
	if result:
		flash('l \'aereo ' + str(aereo_id) + ' è stato cancellato con successo', 'success')
	
	return redirect(url_for('dashboard.dashboardhome'))

@dashboard.route("/dashboardhome", methods=['GET', 'POST'])
@login_required(role="admin")
def dashboardhome():
	flightForm = FlightForm()		#Per aggiunta volo
	planeForm = PlaneForm()			#Per aggiunta aereo
	airportForm = AirportForm()		#Per aggiunta aeroporto

	conn = engine.connect()
	aeroporti = conn.execute("SELECT id, nome, indirizzo FROM aeroporti").fetchall()	#Informazioni necessarie per aeroporti 
	aerei = conn.execute("SELECT id, nome, numeroPosti FROM aerei").fetchall()			#Informazioni necessarie per aerei 
	voli = conn.execute("SELECT * FROM voli NATURAL JOIN pren_volo").fetchall()			#Informazioni necessarie per voli compreso il numero di prenotazioni 
	conn.close()

	#Crea le scelte possibili per i select field visibili nel modal per l'inserimento
	#In questo modo non è possibile inserire un aeroporto o un aereo sbagliato
	#La lista di scelte è composta da coppie (chiave, valore)
	opzioniAeroporti = [(str(choice[0]), str(choice[1]+", "+choice[2]+" #"+str(choice[0]))) for choice in aeroporti]	#Chiave = id aeroporto, Valore = "nome + indirizzo + id"
	flightForm.aeroportoPartenza.choices = [('','')] + opzioniAeroporti					#Imposta le scelte più una scelta vuota per il placeholder
	flightForm.aeroportoArrivo.choices = [('','')] + opzioniAeroporti

	opzioniAerei = [(str(choice[0]), str(choice[1]+" #"+str(choice[0]))) for choice in aerei]	#Chiave = id aereo, Valore "nome + id"
	flightForm.aereo.choices = [('','')]  + opzioniAerei
	
	time = datetime.now()		#Data corrente 

	flightForm.check = False;	#Check per definire se il form è per l'inserimento o la modifica (False -> inserimento)

	if flightForm.is_submitted() and flightForm.submitFlight.data:	#Controlla che sia stato premuto il tasto submit per aggiungere un volo
		if flightForm.validate():									#Valida i dati
			dataOraPartenza = datetime.combine(flightForm.dataPartenza.data, flightForm.oraPartenza.data)	#Combina la data e l'ora inserite nel form
			if flightForm.oraPartenza.data > flightForm.oraArrivo.data:										#l'ora di arrivo precedente all'ora di partenza
				dataOraArrivo = datetime.combine(flightForm.dataPartenza.data + timedelta(days=1), flightForm.oraArrivo.data) #Aggiunge un giorno per la data di arrivo e combina i due campi
			else:
				dataOraArrivo = datetime.combine(flightForm.dataPartenza.data, flightForm.oraArrivo.data)	#combina i due campi

			conn = engine.connect()
			
			#Inserisce il volo
			conn.execute("INSERT INTO voli (aeroportoPartenza, dataOraPartenza, aeroportoArrivo, dataOraArrivo, aereo,prezzo) VALUES (%s,%s,%s,%s,%s,%s)", 
				flightForm.aeroportoPartenza.data, 
				dataOraPartenza, 
				flightForm.aeroportoArrivo.data, 
				dataOraArrivo, 
				flightForm.aereo.data,
				flightForm.prezzo.data
			)
			conn.close()
		   
			flash('Aggiunta volo completata con successo :D', 'success')
			return redirect('dashboardhome')
		else:
			flash('Qualcosa nell\'inserimento del volo è andato storto :(', 'danger')
	
	if planeForm.is_submitted() and planeForm.submitPlane.data:			#Controlla che sia stato premuto il tasto submit per aggiungere un aereo
		if planeForm.validate():
			conn = engine.connect()
			conn.execute("INSERT INTO aerei (nome, numeroPosti) VALUES (%s, %s)", planeForm.nome.data, planeForm.nPosti.data)

			conn.close()

			flash('Aggiunta aereo completata con successo :)', 'success')
			return redirect('dashboardhome')
		else:
			flash('Qualcosa nell\'inserimento dell\'aereo è andato storto :(', 'danger')
	
	if airportForm.is_submitted() and airportForm.submitAirport.data:	#Controlla che sia stato premuto il tasto submit per aggiungere un aeroporto
		if airportForm.validate():
			conn = engine.connect()
			conn.execute("INSERT INTO aeroporti (nome, indirizzo) VALUES (%s, %s)", airportForm.nome.data, airportForm.indirizzo.data)

			conn.close()

			flash('Aggiunta aeroporto completata con successo :D', 'success')
			return redirect('dashboardhome')
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

	updateForm.check = True		#Check True -> form per modifica volo
	
	if updateForm.validate_on_submit():
		
		conn = engine.connect()
		
		conn.execute("UPDATE voli SET aeroportoPartenza=%s, dataOraPartenza=%s, aeroportoArrivo=%s, dataOraArrivo=%s, aereo=%s, prezzo=%s WHERE id = %s", 
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
		return redirect('dashboardhome')
	elif request.method == 'GET': #Imposta le informazini del volo in ogni campo
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
		return redirect('dashboardhome')
	elif request.method == 'GET':	#Imposta le informazini dell' aeroporto in ogni campo
		updateform.nome.data = aeroporto[1]
		updateform.indirizzo.data = aeroporto[2]
		
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
		return redirect('dashboardhome')
	elif request.method == 'GET':	#Imposta le informazini dell' aereo in ogni campo
		updateform.nome.data = aereo[1]
		updateform.nPosti.data = aereo[2]

	return render_template('dashboard_aereo.html', aereo=aereo, planeForm=updateform)