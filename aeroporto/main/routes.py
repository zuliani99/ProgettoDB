from flask import Blueprint, render_template
from sqlalchemy.sql import *
from aeroporto.table import engine
from datetime import datetime
from aeroporto.main.forms import SearchFlyForm

main = Blueprint('main', __name__)


@main.route("/", methods=['GET', 'POST'])
@main.route("/home", methods=['GET', 'POST'])
def home():
	searchForm = SearchFlyForm()

	andata=ritorno=[]
	is_return = False

	conn = engine.connect()
	aeroporti = conn.execute("SELECT id, nome, indirizzo FROM aeroporti").fetchall()
		
	opzioniAeroporti = [(str(choice[0]), str(choice[1]+", "+choice[2])) for choice in aeroporti]
	searchForm.aeroportoPartenza.choices = [('','')] + opzioniAeroporti
	searchForm.aeroportoArrivo.choices = [('','')] + opzioniAeroporti

	if searchForm.validate_on_submit():
		aPart = searchForm.aeroportoPartenza.data
		aArr = searchForm.aeroportoArrivo.data
		dPart = searchForm.dataPartenza.data
		dRit = searchForm.dataRitorno.data
		is_return = searchForm.checkAndataRitorno.data

		#print(str(aPart) + " " + str(dPart)  + " " + str(aArr) + " " + str(dRit) + " " + str(is_return))
		queryandata = "SELECT v.id , part.nome, v.dataOraPartenza, arr.nome, v.dataOraArrivo, v.prezzo FROM voli v, aeroporti arr, aeroporti part, aerei a WHERE v.aeroportoArrivo = arr.id AND v.aeroportoPartenza = part.id AND v.aereo = a.id AND part.id = "+str(aPart)+" AND arr.id = "+str(aArr)+" AND v.dataOraPartenza BETWEEN '"+str(dPart)+" 00:00:00' AND '"+str(dPart)+" 23:59:59'"
		#print(query)
		andata = conn.execute(queryandata).fetchall()

		if dRit is not None:
			queryritorno = "SELECT v.id , part.nome, v.dataOraPartenza, arr.nome, v.dataOraArrivo, v.prezzo FROM voli v, aeroporti arr, aeroporti part, aerei a WHERE v.aeroportoArrivo = arr.id AND v.aeroportoPartenza = part.id AND v.aereo = a.id AND part.id = "+str(aArr)+" AND arr.id = "+str(aPart)+" AND v.dataOraPartenza BETWEEN '"+str(dRit)+" 00:00:00' AND '"+str(dRit)+" 23:59:59'"
			ritorno = conn.execute(queryritorno).fetchall()


	else:
		andata = conn.execute("SELECT v.id , part.nome, v.dataOraPartenza, arr.nome, v.dataOraArrivo, v.prezzo FROM voli v, aeroporti arr, aeroporti part, aerei a WHERE v.aeroportoArrivo = arr.id and v.aeroportoPartenza = part.id and v.aereo = a.id and v.dataOraPartenza > %s ORDER BY v.dataOraPartenza ASC", datetime.utcnow()).fetchall()
		
	#print(str(is_return))
	conn.close()
	return render_template('home.html', voliand=andata, volirit=ritorno, flyForm=searchForm, is_return=is_return)
	#, page=page, mp=math.ceil(m[0]/5))

@main.route("/about") #mi renderizza il template about.html con variabuile title='About'
def about():
	return render_template('about.html', title='About')
