from flask import render_template, url_for, flash, redirect, abort, Blueprint #import necessari per il funzionamento dell'applicazione
from aeroporto.fly.forms import AddBookingGone, AddBookingReturn
from flask_login import current_user
from aeroporto.table import User, users, engine, load_user, voli, aerei, aeroporti
from sqlalchemy.sql import *
from aeroporto.fly.utils import send_ticket_notify, get_available_sit
from aeroporto.main.utils import login_required


fly = Blueprint('fly', __name__)



@fly.route("/gone<int:volopart>", methods=['GET', 'POST'])
#@login_required(role="customer")
def gone(volopart):
	formGone = AddBookingGone()
	conn = engine.connect()
	#trans = conn.begin()

	volo = conn.execute("SELECT v.id , part.nome, v.dataOraPartenza, arr.nome, v.dataOraArrivo, v.prezzo, a.numeroPosti, a.numeroPosti-pv.pren as postdisp FROM voli v, aeroporti arr, aeroporti part, aerei a, pren_volo pv WHERE v.aeroportoArrivo = arr.id and v.aeroportoPartenza = part.id and v.aereo = a.id and pv.id = v.id and v.id = %s",volopart).fetchone()
	#print("SELECT v.id , part.nome, v.dataOraPartenza, arr.nome, v.dataOraArrivo, v.prezzo, a.numeroPosti, a.numeroPosti-pv.pren as postdisp FROM voli v, aeroporti arr, aeroporti part, aerei a, pren_volo pv WHERE v.aeroportoArrivo = arr.id and v.aeroportoPartenza = part.id and v.aereo = a.id and pv.id = v.id and v.id = "+volopart)
	pocc = conn.execute("SELECT p.numeroPosto FROM voli v JOIN prenotazioni p ON v.id = p.id_volo WHERE v.id = %s",volopart).fetchall()
	conn.close()
	
	available_sits = get_available_sit(pocc,volo)

	conn = engine.connect()

	bagagli = conn.execute("SELECT prezzo, descrizione FROM bagagli").fetchall()
	formGone.bagaglioAndata.choices = [(str(bag[0]), str(bag[1])) for bag in bagagli]
	conn.close()

	if formGone.validate_on_submit():
		if current_user.is_authenticated:
			if load_user(current_user.id).get_urole() == "customer":
				conn = engine.connect()
				#print("INSERT INTO prenotazioni (id_user, id_volo, numeroPosto, prezzo_bagaglio) VALUES ( "+str(current_user.id)+","+ str(volopart)+","+ formGone.postoAndata.data+","+ formGone.bagaglioAndata.data+")")
				trans = conn.begin()
				try:
					conn.execute("INSERT INTO prenotazioni (id_user, id_volo, numeroPosto, prezzo_bagaglio) VALUES (%s, %s, %s, %s)",
						current_user.id,
						volopart,
						formGone.postoAndata.data,
						formGone.bagaglioAndata.data
					)
					trans.commit()
					bagAndata = conn.execute("SELECT * FROM bagagli WHERE prezzo = %s", formGone.bagaglioAndata.data).fetchone()

					#send_ticket_notify(volo, formGone.postoAndata.data, bagAndata, 0, 0, 0)
						
					flash('Acquisto completato. Ti abbiamo inviato una mail con tutte le informazioni del biglietto', 'success')
					return redirect(url_for('user_fly'))
				except:
					trans.rollback()
					flash("Posto da sedere appena acquistato, scegliene un altro", 'warning')
				finally:
					conn.close()
			else:
				flash("Devi essere un cliente acquistare il biglietto", 'warning')
		else:
			flash("Devi accedere al tuo account per acquistare il biglietto", 'danger')
			return redirect(url_for('login'))
	return render_template('volo.html', title=volopart, volo=volo, form=formGone, free=available_sits)




@fly.route("/roundtrip/<int:volopart>/<int:volorit>", methods=['GET', 'POST'])
#@login_required(role="customer")
def roundtrip(volopart, volorit):
	formRoundtrip = AddBookingReturn()
	conn = engine.connect()
	#trans = conn.begin()

	andata = conn.execute("SELECT v.id , part.nome, v.dataOraPartenza, arr.nome, v.dataOraArrivo, v.prezzo, a.numeroPosti, a.numeroPosti-pv.pren as postdisp FROM voli v, aeroporti arr, aeroporti part, aerei a, pren_volo pv WHERE v.aeroportoArrivo = arr.id and v.aeroportoPartenza = part.id and v.aereo = a.id and pv.id = v.id and v.id = %s",volopart).fetchone()
	#print("SELECT v.id , part.nome, v.dataOraPartenza, arr.nome, v.dataOraArrivo, v.prezzo, a.numeroPosti, a.numeroPosti-pv.pren as postdisp FROM voli v, aeroporti arr, aeroporti part, aerei a, pren_volo pv WHERE v.aeroportoArrivo = arr.id and v.aeroportoPartenza = part.id and v.aereo = a.id and pv.id = v.id and v.id = "+volopart)
	poccandata = conn.execute("SELECT p.numeroPosto FROM voli v JOIN prenotazioni p ON v.id = p.id_volo WHERE v.id = %s",volopart).fetchall()
	
	available_groups_gone = get_available_sit(poccandata, andata)

	ritorno = conn.execute("SELECT v.id , part.nome, v.dataOraPartenza, arr.nome, v.dataOraArrivo, v.prezzo, a.numeroPosti, a.numeroPosti-pv.pren as postdisp FROM voli v, aeroporti arr, aeroporti part, aerei a, pren_volo pv WHERE v.aeroportoArrivo = arr.id and v.aeroportoPartenza = part.id and v.aereo = a.id and pv.id = v.id and v.id = %s",volorit).fetchone()
	poccritorno = conn.execute("SELECT p.numeroPosto FROM voli v JOIN prenotazioni p ON v.id = p.id_volo WHERE v.id = %s",volorit).fetchall()
	
	available_groups_return = get_available_sit(poccritorno,ritorno)

	bagagli = conn.execute("SELECT prezzo, descrizione FROM bagagli").fetchall()
	formRoundtrip.bagaglioAndata.choices = [(str(b[0]), str(b[1])) for b in bagagli]
	formRoundtrip.bagaglioRitorno.choices = [(str(b[0]), str(b[1])) for b in bagagli]
	conn.close()

	if formRoundtrip.validate_on_submit():
		if current_user.is_authenticated:
			if load_user(current_user.id).get_urole() == "customer":
				conn = engine.connect()
				trans = conn.begin()
				try:
					conn.execute("INSERT INTO prenotazioni (id_user, id_volo, numeroPosto, prezzo_bagaglio) VALUES (%s, %s, %s, %s),(%s, %s, %s, %s)", 
						current_user.id,
						andata[0],
						formRoundtrip.postoAndata.data,
						formRoundtrip.bagaglioAndata.data,
						current_user.id,
						ritorno[0],
						formRoundtrip.postoRitorno.data,
						formRoundtrip.bagaglioRitorno.data
					)
					bagAndata = conn.execute("SELECT * FROM bagagli WHERE prezzo = %s", formRoundtrip.bagaglioAndata.data).fetchone()
					bagRitorno = conn.execute("SELECT * FROM bagagli WHERE prezzo = %s", formRoundtrip.bagaglioRitorno.data).fetchone()
					
					send_ticket_notify(andata, formRoundtrip.postoAndata.data, bagAndata, ritorno, formRoundtrip.postoRitorno.data, bagRitorno)
					
					flash('Acquisto completato. Ti abbiamo inviato una mail con tutte le informazioni dei biglietti', 'success')
					trans.commit()
					return redirect(url_for('user_fly'))
					#possiamo modificare la tabella escludendo la prima select ed aggiungendo le transazioni
				##else:
				except:
					'''if verposto1 is not None:
						flash("Posto da sedere per l'andata appena acquistato, scegliene un altro", 'warning')
					if verposto2 is not None:
						flash("Posto da sedere per il ritorno appena acquistato, scegliene un altro", 'warning')'''
					flash("Attenzione posto da sedere per l'andata o rtitorno appena acquistato, sceglierne un altro", "warning")
				finally:
					conn.close()
			else:
				flash("Devi essere un cliente acquistare il biglietto", 'warning')
				#return redirect(url_for('roundtrip'))
		else:
			flash("Devi accedere al tuo account per acquistare il biglietto", 'danger')
			return redirect(url_for('login'))
	return render_template('voli.html', title=str(volopart) + " / " + str(volorit), volopart=andata, volorit=ritorno, form=formRoundtrip, freegone=available_groups_gone, freereturn=available_groups_return)


	



@fly.route("/delete_fly<int:fly_id>", methods=['GET', 'POST'])
@login_required(role="customer")
def delete_fly(fly_id):
	conn = engine.connect()
	pren = conn.execute("SELECT * FROM prenotazioni WHERE id = %s",fly_id).fetchone()
	if pren is None:
		abort(404)
	if pren[1] != current_user.id:
		abort(403)
   
	conn.execute("DELETE FROM prenotazioni WHERE id = %s", fly_id)
	flash('Il volo ' + str(pren[0]) + ' da te prenotato è stato cancellato con successo', 'success')
	conn.close()
	return redirect(url_for('user_fly'))





@fly.route("/review_fly<int:fly_id>,<int:val>,<crit>", methods=['GET', 'POST'])
@login_required(role="customer")
def review_fly(fly_id, val, crit):
	conn = engine.connect()
	pren = conn.execute("SELECT * FROM prenotazioni WHERE id = %s",fly_id).fetchone()
	if pren is None:
		abort(404)
	if pren[1] != current_user.id:
		abort(403)

	val = conn.execute("SELECT valutazione FROM prenotazioni WHERE id = %s", fly_id).fetchone()
	if val[0] is None: 
		conn.execute("UPDATE prenotazioni SET valutazione = %s , critiche = %s WHERE id = %s", val, crit, fly_id)
		conn.close()
		flash("Recensione inserita con successo", "success")
	else:
		flash("Recensione già inserita con successo", "warning")
	return redirect(url_for('user_fly'))