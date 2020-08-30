from flask import render_template, url_for, flash, redirect, abort, Blueprint
from aeroporto.fly.forms import AddBookingGone, AddBookingReturn
from flask_login import current_user
from aeroporto.table import User, users, engine, load_user, voli, aerei, aeroporti
from sqlalchemy.sql import *
from aeroporto.fly.utils import send_ticket_notify, get_available_sit
from aeroporto.main.utils import login_required


# Utilizzo di Blueprint per mappare il progetto in gruppi di funzionalità
fly = Blueprint('fly', __name__)


# Route per l'aggiunta di una prenotazione di un volo di sola andata
@fly.route("/gone<int:volopart>", methods=['GET', 'POST'])
def gone(volopart):
	formGone = AddBookingGone() # Richiamo il from
	conn = engine.connect()

	# Restituisco tutte le particolari informazioni per il volo
	volo = conn.execute(
		"SELECT v.id , part.nome, v.dataOraPartenza, arr.nome, v.dataOraArrivo, v.prezzo, a.numeroPosti, a.numeroPosti-pv.pren as postdisp " + 
		"FROM voli v, aeroporti arr, aeroporti part, aerei a, pren_volo pv WHERE v.aeroportoArrivo = arr.id and v.aeroportoPartenza = part.id and v.aereo = a.id and pv.id = v.id and v.id = %s",volopart
	).fetchone()
	# Restituisco i posti occupati per il volo che voglio prenotare
	pocc = conn.execute("SELECT p.numeroPosto FROM voli v JOIN prenotazioni p ON v.id = p.id_volo WHERE v.id = %s",volopart).fetchall()
	
	# Richiamo la funzione get_available_sit che mi restituisce la lista dei posti disponibili per il volo che voglio acquistare
	available_sits = get_available_sit(pocc,volo)

	# Restituisco i bagagli disponibili e li inserisco nel SelectField  del from fromGone
	bagagli = conn.execute("SELECT prezzo, descrizione FROM bagagli").fetchall()
	formGone.bagaglioAndata.choices = [(str(bag[0]), str(bag[1])) for bag in bagagli]
	conn.close()

	if formGone.validate_on_submit():
		# Se l'utente è autenticato
		if current_user.is_authenticated:
			# Se l'utente è un cliente
			if load_user(current_user.id).get_urole() == "customer":
				# Creo una connessione ed una transazione
				conn = engine.connect()
				trans = conn.begin()
				try:
					# Inserisco la prenotazione nella tabella prenotazioni con i suoli campi necessari
					conn.execute("INSERT INTO prenotazioni (id_user, id_volo, numeroPosto, prezzo_bagaglio, prezzotot) VALUES (%s, %s, %s, %s, %s)",
						current_user.id,
						volopart,
						formGone.postoAndata.data,
						formGone.bagaglioAndata.data,
						float(volo[5])+float(formGone.bagaglioAndata.data)
					)


					# Restituisco la descrizione del bagaglio che l'utente ha scelto
					bagAndata = conn.execute("SELECT * FROM bagagli WHERE prezzo = %s", formGone.bagaglioAndata.data).fetchone()

					# Richiamo la funzione send_ticket_notify per invisare una mail all'utente di avvenuta prenotazione del tocket con tutte le informazioni necessarie per l'imbarco
					send_ticket_notify(volo, formGone.postoAndata.data, bagAndata, 0, 0, 0)
					# Committo la transazione
					trans.commit()
					flash('Acquisto completato. Ti abbiamo inviato una mail con tutte le informazioni del biglietto', 'success')
					return redirect(url_for('users.user_fly'))
				except:
					# Se la transazione ha restituito un errore esegui una rollback
					trans.rollback()
					flash("Posto da sedere appena acquistato, scegliene un altro", 'warning')
				finally:
					conn.close()
			else:
				# Solo i clienti possono acquistare biglietti
				flash("Devi essere un cliente acquistare il biglietto", 'warning')
		else:
			flash("Devi accedere al tuo account per acquistare il biglietto", 'danger')
			return redirect(url_for('users.login'))
	return render_template('volo.html', title=volopart, volo=volo, form=formGone, free=available_sits)




# Route per l'aggiunta di una prenotazione di un volo di andata e ritorno
@fly.route("/roundtrip/<int:volopart>/<int:volorit>", methods=['GET', 'POST'])
def roundtrip(volopart, volorit):
	formRoundtrip = AddBookingReturn()
	conn = engine.connect()

	# Restituisco tutte le particolari informazioni per il volo di andata
	andata = conn.execute(
		"SELECT v.id , part.nome, v.dataOraPartenza, arr.nome, v.dataOraArrivo, v.prezzo, a.numeroPosti, a.numeroPosti-pv.pren as postdisp " + 
		"FROM voli v, aeroporti arr, aeroporti part, aerei a, pren_volo pv WHERE v.aeroportoArrivo = arr.id and v.aeroportoPartenza = part.id and v.aereo = a.id and pv.id = v.id and v.id = %s",volopart
	).fetchone()
	# Restituisco i posti occupati per il volo di andata che voglio prenotare
	poccandata = conn.execute("SELECT p.numeroPosto FROM voli v JOIN prenotazioni p ON v.id = p.id_volo WHERE v.id = %s",volopart).fetchall()
	# Richiamo la funzione get_available_sit che mi restituisce la lista dei posti disponibili per il volo di andata che voglio acquistare
	available_groups_gone = get_available_sit(poccandata, andata)


	# Restituisco tutte le particolari informazioni per il volo di ritorno
	ritorno = conn.execute(
		"SELECT v.id , part.nome, v.dataOraPartenza, arr.nome, v.dataOraArrivo, v.prezzo, a.numeroPosti, a.numeroPosti-pv.pren as postdisp " +
		"FROM voli v, aeroporti arr, aeroporti part, aerei a, pren_volo pv WHERE v.aeroportoArrivo = arr.id and v.aeroportoPartenza = part.id and v.aereo = a.id and pv.id = v.id and v.id = %s",volorit
	).fetchone()
	# Restituisco i posti occupati per il volo di ritorno che voglio prenotare
	poccritorno = conn.execute("SELECT p.numeroPosto FROM voli v JOIN prenotazioni p ON v.id = p.id_volo WHERE v.id = %s",volorit).fetchall()
	# Richiamo la funzione get_available_sit che mi restituisce la lista dei posti disponibili per il volo di ritorno che voglio acquistare
	available_groups_return = get_available_sit(poccritorno,ritorno)

	# Restituisco i bagagli disponibili e li inserisco nel SelectField del from formRoundtrip
	bagagli = conn.execute("SELECT prezzo, descrizione FROM bagagli").fetchall()
	formRoundtrip.bagaglioAndata.choices = [(str(b[0]), str(b[1])) for b in bagagli]
	formRoundtrip.bagaglioRitorno.choices = [(str(b[0]), str(b[1])) for b in bagagli]
	conn.close()

	if formRoundtrip.validate_on_submit():
		# Se l'utente è autenticato
		if current_user.is_authenticated:
			# Se l'utente è un cliente
			if load_user(current_user.id).get_urole() == "customer":
				# Creo una connessione ed una transazione
				conn = engine.connect()
				trans = conn.begin()
				try:
					# Inserisco la prenotazione nella tabella prenotazioni con i suoli campi necessari
					conn.execute("INSERT INTO prenotazioni (id_user, id_volo, numeroPosto, prezzo_bagaglio, prezzotot) VALUES (%s, %s, %s, %s),(%s, %s, %s, %s)", 
						current_user.id,
						andata[0],
						formRoundtrip.postoAndata.data,
						formRoundtrip.bagaglioAndata.data,
						float(andata[5])+float(formGone.bagaglioAndata.data),
						current_user.id,
						ritorno[0],
						formRoundtrip.postoRitorno.data,
						formRoundtrip.bagaglioRitorno.data,
						float(ritorno[5])+float(formRoundtrip.bagaglioRitorno.data)
					)
					# Committo la transazione
					trans.commit()

					# Restituisco la descrizione del bagaglio che l'utente ha scelto
					bagAndata = conn.execute("SELECT * FROM bagagli WHERE prezzo = %s", formRoundtrip.bagaglioAndata.data).fetchone()
					bagRitorno = conn.execute("SELECT * FROM bagagli WHERE prezzo = %s", formRoundtrip.bagaglioRitorno.data).fetchone()
					
					# Richiamo la funzione send_ticket_notify per invisare una mail all'utente di avvenuta prenotazione del tocket con tutte le informazioni necessarie per l'imbarco
					send_ticket_notify(andata, formRoundtrip.postoAndata.data, bagAndata, ritorno, formRoundtrip.postoRitorno.data, bagRitorno)
					
					flash('Acquisto completato. Ti abbiamo inviato una mail con tutte le informazioni dei biglietti', 'success')
					return redirect(url_for('users.user_fly'))
				except:
					# Se la transazione ha restituito un errore esegui una rollback
					flash("Attenzione posto da sedere per l'andata o rtitorno appena acquistato, sceglierne un altro", "warning")
				finally:
					conn.close()
			else:
				# Solo i clienti possono acquistare biglietti
				flash("Devi essere un cliente acquistare il biglietto", 'warning')
		else:
			flash("Devi accedere al tuo account per acquistare il biglietto", 'danger')
			return redirect(url_for('users.login'))
	return render_template('voli.html', title=str(volopart) + " / " + str(volorit), volopart=andata, volorit=ritorno, form=formRoundtrip, freegone=available_groups_gone, freereturn=available_groups_return)


	


# Route per l'eliminazione di una prenotazione 
@fly.route("/delete_fly<int:fly_id>", methods=['GET', 'POST'])
@login_required(role="customer")
def delete_fly(fly_id):
	# Stabilisco una connessione
	conn = engine.connect()
	# Restituisco la prenotazione che si vuole eliminare
	pren = conn.execute("SELECT * FROM prenotazioni WHERE id = %s",fly_id).fetchone()
	# Se la prenotazione non esiste si abortisce
	if pren is None:
		abort(404)
	# Se l'utente che ha richiesto l'eliminazione non è lo stesso che l'ha effettuata si abortisce
	if pren[1] != current_user.id:
		abort(403)
   
   	# Eliminazione effettiva della prenotazione
	conn.execute("DELETE FROM prenotazioni WHERE id = %s", fly_id)
	flash('Il volo ' + str(pren[0]) + ' da te prenotato è stato cancellato con successo', 'success')
	conn.close()
	return redirect(url_for('users.user_fly'))



# Route per l'aggiunta di una recesione al volo
@fly.route("/review_fly<int:fly_id>,<int:voto>,<crit>", methods=['GET', 'POST'])
@login_required(role="customer")
def review_fly(fly_id, voto, crit):
	# Stabilisco una connessione
	conn = engine.connect()
	# Restituisco la prenotazione che si vuole recensire
	pren = conn.execute("SELECT * FROM prenotazioni WHERE id = %s",fly_id).fetchone()
	# Se la prenotazione non esiste si abortisce
	if pren is None:
		abort(404)
		# Se l'utente che ha richiesto la prenotazione non è lo stesso che l'ha effettuata si abortisce
	if pren[1] != current_user.id:
		abort(403)

	# Se si è già fatta una recensione per quella prenotazione non è più possibile farla
	val = conn.execute("SELECT valutazione FROM prenotazioni WHERE id = %s", fly_id).fetchone()
	if val[0] is None: 
		# Inserimento della recensione 
		conn.execute("UPDATE prenotazioni SET valutazione = %s , critiche = %s WHERE id = %s", voto, crit, fly_id)
		conn.close()
		flash("Recensione inserita con successo", "success")
	else:
		flash("Recensione già inserita con successo", "warning")
	return redirect(url_for('users.user_fly'))