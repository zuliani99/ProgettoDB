from flask import render_template, url_for, flash, redirect, request, Blueprint#import necessari per il funzionamento dell'applicazione
from aeroporto.statistics.forms import StatisticsForm
from aeroporto.table import engine, voli, aerei, aeroporti, deleteElementByID
from sqlalchemy.sql import *
from aeroporto.main.utils import login_required

statistics = Blueprint('statistics', __name__)


@statistics.route("/statisticsHome", methods=['GET', 'POST'])
@login_required(role = "admin")
def statisticsHome():
	statisticsForm = StatisticsForm()

	conn = engine.connect()

	#Read uncommitted non avendo necessità di leggere i dati precisi per le statistiche
	conn = conn.execution_options(
    	isolation_level="READ UNCOMMITTED"
	)

	#Numero totale di passeggeri
	totPasseggeri = conn.execute("SELECT IFNULL(sum(pren),0) FROM pren_volo JOIN voli ON pren_volo.id = voli.id WHERE voli.dataOraArrivo < CURRENT_DATE").fetchone()

	#Passeggeri totali nell'ultimo mese
	totPasMesePrec = conn.execute(
		"SELECT IFNULL(sum(pren), 0) FROM voli NATURAL JOIN pren_volo WHERE voli.dataOraPartenza BETWEEN (CURRENT_DATE() - INTERVAL 1 MONTH) AND CURRENT_DATE()"
	).fetchone()
	totPasMeseSucc = conn.execute(
		"SELECT IFNULL(sum(pren), 0) FROM voli NATURAL JOIN pren_volo WHERE voli.dataOraPartenza BETWEEN CURRENT_DATE() AND (CURRENT_DATE() + INTERVAL 1 MONTH)"
	).fetchone()
	#Guadagni totali calcolati sulla somma del prezzo delle prenotazioni
	guadagniTotali = conn.execute("SELECT IFNULL(sum(prenotazioni.prezzotot),0) FROM prenotazioni").fetchone()

	#Ritorna la lista di aeroporti con nome e il numero totale di passeggeri arrivati e in partenza
	infoAeroporti = conn.execute(
		"SELECT nomeA, partenze, arrivi "+
		"FROM (SELECT a.nome as nomeA, IFNULL(SUM(pren_volo.pren), 0) AS partenze "+
					"FROM aeroporti AS a LEFT JOIN voli ON a.id = voli.aeroportoPartenza LEFT JOIN pren_volo ON voli.id = pren_volo.id "+
					"GROUP BY a.nome) AS t1,"+
					"(SELECT a.nome as nomeB, IFNULL(SUM(pren_volo.pren), 0)AS arrivi "+
					"FROM aeroporti AS a LEFT JOIN voli ON a.id = voli.aeroportoArrivo LEFT JOIN pren_volo ON voli.id = pren_volo.id "+
					"GROUP BY a.nome) AS t2 "+
		"WHERE nomeA = nomeB").fetchall()

	#Ritorna la tratta del volo con il rapporto fra il numero di prenotazioni e posti totali e la media delle valutazioni (0 se non ci sono valutazioni) 
	infoVoli = conn.execute(
		"SELECT a1.nome, a2.nome, aerei.nome, (pren_volo.pren/aerei.numeroPosti)*100 AS percentualeCarico, IFNULL(AVG(prenotazioni.valutazione),0) AS valutazioneMedia, voli.dataOraArrivo "+
		"FROM voli JOIN aeroporti AS a1 on voli.aeroportoPartenza = a1.id "+
						"JOIN aeroporti AS a2 ON voli.aeroportoArrivo = a2.id "+
						"JOIN aerei ON voli.aereo = aerei.id JOIN pren_volo ON voli.id = pren_volo.id "+
						"LEFT JOIN prenotazioni on voli.id = prenotazioni.id_volo "+
		"GROUP BY voli.id").fetchall()


	if statisticsForm.validate_on_submit():
		dataDa = statisticsForm.dataA.data
		dataA = statisticsForm.dataB.data

		#Ha inserito un filtro con dataInizio e dataFine per il calcolo delle informazioni
		if dataDa is not None and dataA is not None:
			infoAeroporti = conn.execute(
				"SELECT nomeA, partenze, arrivi "+
				"FROM (SELECT a.nome as nomeA, IFNULL(SUM(pren_volo.pren), 0) AS partenze "+
					  "FROM aeroporti AS a LEFT JOIN voli ON a.id = voli.aeroportoPartenza LEFT JOIN pren_volo ON voli.id = pren_volo.id "+
					  "WHERE voli.dataOraPartenza >= %s AND voli.dataOraArrivo <= %s"+
					  "GROUP BY a.nome) AS t1,"+
					  "(SELECT a.nome as nomeB, IFNULL(SUM(pren_volo.pren), 0)AS arrivi "+
					  "FROM aeroporti AS a LEFT JOIN voli ON a.id = voli.aeroportoArrivo LEFT JOIN pren_volo ON voli.id = pren_volo.id "+
					  "WHERE voli.dataOraPartenza >= %s AND voli.dataOraArrivo <= %s"+
					  "GROUP BY a.nome) AS t2 "+
				"WHERE nomeA = nomeB", dataDa, dataA, dataDa, dataA).fetchall()

			infoVoli = conn.execute(
				"SELECT a1.nome, a2.nome, aerei.nome, (pren_volo.pren/aerei.numeroPosti)*100 AS percentualeCarico, IFNULL(AVG(prenotazioni.valutazione),0) AS valutazioneMedia, voli.dataOraArrivo "+
				"FROM voli JOIN aeroporti AS a1 on voli.aeroportoPartenza = a1.id "+
						  "JOIN aeroporti AS a2 ON voli.aeroportoArrivo = a2.id "+
						  "JOIN aerei ON voli.aereo = aerei.id JOIN pren_volo ON voli.id = pren_volo.id "+
						  "LEFT JOIN prenotazioni on voli.id = prenotazioni.id_volo "+
				"WHERE voli.dataOraPartenza >= %s AND voli.dataOraArrivo <= %s"+
				"GROUP BY voli.id", dataDa, dataA).fetchall()

		#Ha inserito solo la data fine, quindi calcola le informazioni sulle tuple con data precendente a quella
		elif dataDa is None and dataA is not None:
			infoAeroporti = conn.execute(
				"SELECT nomeA, partenze, arrivi "+
				"FROM (SELECT a.nome as nomeA, IFNULL(SUM(pren_volo.pren), 0) AS partenze "+
					  "FROM aeroporti AS a LEFT JOIN voli ON a.id = voli.aeroportoPartenza LEFT JOIN pren_volo ON voli.id = pren_volo.id "+
					  "WHERE voli.dataOraArrivo <= %s"+
					  "GROUP BY a.nome) AS t1,"+
					  "(SELECT a.nome as nomeB, IFNULL(SUM(pren_volo.pren), 0)AS arrivi "+
					  "FROM aeroporti AS a LEFT JOIN voli ON a.id = voli.aeroportoArrivo LEFT JOIN pren_volo ON voli.id = pren_volo.id "+
					  "WHERE voli.dataOraArrivo <= %s"+
					  "GROUP BY a.nome) AS t2 "+
				"WHERE nomeA = nomeB", dataA, dataA).fetchall()

			infoVoli = conn.execute(
				"SELECT a1.nome, a2.nome, aerei.nome, (pren_volo.pren/aerei.numeroPosti)*100 AS percentualeCarico, IFNULL(AVG(prenotazioni.valutazione),0) AS valutazioneMedia, voli.dataOraArrivo "+
				"FROM voli JOIN aeroporti AS a1 on voli.aeroportoPartenza = a1.id "+
						  "JOIN aeroporti AS a2 ON voli.aeroportoArrivo = a2.id "+
						  "JOIN aerei ON voli.aereo = aerei.id JOIN pren_volo ON voli.id = pren_volo.id "+
						  "LEFT JOIN prenotazioni on voli.id = prenotazioni.id_volo "+
				"WHERE voli.dataOraArrivo<= %s"+
				"GROUP BY voli.id", dataA).fetchall()

		#Ha inserito solo la data fine, quindi calcola le informazioni su tutte le tuple con data successiva a quella
		elif dataDa is not None and dataA is None:
			infoAeroporti = conn.execute(
				"SELECT nomeA, partenze, arrivi "+
				"FROM (SELECT a.nome as nomeA, IFNULL(SUM(pren_volo.pren), 0) AS partenze "+
					  "FROM aeroporti AS a LEFT JOIN voli ON a.id = voli.aeroportoPartenza LEFT JOIN pren_volo ON voli.id = pren_volo.id "+
					  "WHERE voli.dataOraPartenza >= %s"+
					  "GROUP BY a.nome) AS t1,"+
					  "(SELECT a.nome as nomeB, IFNULL(SUM(pren_volo.pren), 0)AS arrivi "+
					  "FROM aeroporti AS a LEFT JOIN voli ON a.id = voli.aeroportoArrivo LEFT JOIN pren_volo ON voli.id = pren_volo.id "+
					  "WHERE voli.dataOraPartenza >= %s"+
					  "GROUP BY a.nome) AS t2 "+
				"WHERE nomeA = nomeB", dataDa, dataDa).fetchall()

			infoVoli = conn.execute(
				"SELECT a1.nome, a2.nome, aerei.nome, (pren_volo.pren/aerei.numeroPosti)*100 AS percentualeCarico, IFNULL(AVG(prenotazioni.valutazione),0) AS valutazioneMedia, voli.dataOraArrivo "+
				"FROM voli JOIN aeroporti AS a1 on voli.aeroportoPartenza = a1.id "+
						  "JOIN aeroporti AS a2 ON voli.aeroportoArrivo = a2.id "+
						  "JOIN aerei ON voli.aereo = aerei.id JOIN pren_volo ON voli.id = pren_volo.id "+
						  "LEFT JOIN prenotazioni on voli.id = prenotazioni.id_volo "+
				"WHERE voli.dataOraPartenza >= %s"+
				"GROUP BY voli.id ",dataDa).fetchall()

		#Non ha inserito alcun filtro quindi calcola le informazioni su tutte le tuple
		else:
			infoAeroporti = conn.execute(
				"SELECT nomeA, partenze, arrivi "+
				"FROM (SELECT a.nome as nomeA, IFNULL(SUM(pren_volo.pren), 0) AS partenze "+
					  "FROM aeroporti AS a LEFT JOIN voli ON a.id = voli.aeroportoPartenza LEFT JOIN pren_volo ON voli.id = pren_volo.id "+
					  "GROUP BY a.nome) AS t1,"+
					  "(SELECT a.nome as nomeB, IFNULL(SUM(pren_volo.pren), 0)AS arrivi "+
					  "FROM aeroporti AS a LEFT JOIN voli ON a.id = voli.aeroportoArrivo LEFT JOIN pren_volo ON voli.id = pren_volo.id "+
					  "GROUP BY a.nome) AS t2 "+
				"WHERE nomeA = nomeB").fetchall()

			infoVoli = conn.execute(
				"SELECT a1.nome, a2.nome, aerei.nome, (pren_volo.pren/aerei.numeroPosti)*100 AS percentualeCarico, IFNULL(AVG(prenotazioni.valutazione),0) AS valutazioneMedia, voli.dataOraArrivo "+
				"FROM voli JOIN aeroporti AS a1 on voli.aeroportoPartenza = a1.id "+
						  "JOIN aeroporti AS a2 ON voli.aeroportoArrivo = a2.id "+
						  "JOIN aerei ON voli.aereo = aerei.id JOIN pren_volo ON voli.id = pren_volo.id "+
						  "LEFT JOIN prenotazioni on voli.id = prenotazioni.id_volo "+
				"GROUP BY voli.id").fetchall()

	#Calcola la tratta (partenza, arrivo) con il guadagno massimo 
	trattaGuadagniMax = conn.execute(
		"SELECT IFNULL(aeroportoP, 'None'), IFNULL(aeroportoA, 'None'), IFNULL(guadagniTot,0) FROM guadagniTratte WHERE guadagniTot = (SELECT MAX(guadagniTot) FROM guadagniTratte)"
	).fetchone()

	conn.close()
	return render_template('statistiche.html', title='Statistiche', fromStat = statisticsForm, totPasseggeri = totPasseggeri[0], totPasMesePrec = totPasMesePrec[0], totPasMeseSucc = totPasMeseSucc[0],aeroporti = infoAeroporti, guadagniTot = guadagniTotali[0], trattaGuadagniMax = trattaGuadagniMax, voli=infoVoli)