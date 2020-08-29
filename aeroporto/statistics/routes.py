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

	conn = conn.execution_options(
    	isolation_level="READ UNCOMMITTED"
	)

	#non considerare quelli futuri
	totPasseggeri = conn.execute("SELECT sum(pren) FROM pren_volo").fetchone()

	totPasseggeri_mese = conn.execute("SELECT IFNULL(sum(pren), 0) FROM voli NATURAL JOIN pren_volo WHERE YEAR(dataOraPartenza) = YEAR(CURRENT_DATE - INTERVAL 1 MONTH) AND MONTH(dataOraPartenza) = MONTH(CURRENT_DATE - INTERVAL 1 MONTH)").fetchone()
	
	guadagniTotali = conn.execute("SELECT IFNULL(sum(prenotazioni.prezzotot),0) FROM prenotazioni").fetchone()

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
		"SELECT a1.nome, a2.nome, aerei.nome, pren_volo.pren/aerei.numeroPosti AS percentualeCarico, IFNULL(AVG(prenotazioni.valutazione),0) AS valutazioneMedia, voli.dataOraArrivo "+
		"FROM voli JOIN aeroporti AS a1 on voli.aeroportoPartenza = a1.id "+
						"JOIN aeroporti AS a2 ON voli.aeroportoArrivo = a2.id "+
						"JOIN aerei ON voli.aereo = aerei.id JOIN pren_volo ON voli.id = pren_volo.id "+
						"LEFT JOIN prenotazioni on voli.id = prenotazioni.id_volo "+
		"GROUP BY voli.id HAVING voli.dataOraArrivo <= CURRENT_DATE").fetchall()


	if statisticsForm.validate_on_submit():
		dataDa = statisticsForm.dataA.data
		dataA = statisticsForm.dataB.data

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
				"SELECT a1.nome, a2.nome, aerei.nome, pren_volo.pren/aerei.numeroPosti AS percentualeCarico, IFNULL(AVG(prenotazioni.valutazione),0) AS valutazioneMedia, voli.dataOraArrivo "+
				"FROM voli JOIN aeroporti AS a1 on voli.aeroportoPartenza = a1.id "+
						  "JOIN aeroporti AS a2 ON voli.aeroportoArrivo = a2.id "+
						  "JOIN aerei ON voli.aereo = aerei.id JOIN pren_volo ON voli.id = pren_volo.id "+
						  "LEFT JOIN prenotazioni on voli.id = prenotazioni.id_volo "+
				"WHERE voli.dataOraPartenza >= %s AND voli.dataOraArrivo <= %s"+
				"GROUP BY voli.id HAVING voli.dataOraArrivo <= CURRENT_DATE", dataDa, dataA).fetchall()

		elif dataDa is None and dataA is not None:
			infoAeroporti = conn.execute(
				"SELECT nomeA, partenze, arrivi "+
				"FROM (SELECT a.nome as nomeA, IFNULL(SUM(pren_volo.pren), 0) AS partenze "+
					  "FROM aeroporti AS a LEFT JOIN voli ON a.id = voli.aeroportoPartenza LEFT JOIN pren_volo ON voli.id = pren_volo.id "+
					  "WHERE voli.dataOraArrivo <= %s"+
					  "GROUP BY a.nome) AS t1,"+
					  "(SELECT a.nome as nomeB, IFNULL(SUM(pren_volo.pren), 0)AS arrivi "+
					  "FROM aeroporti AS a LEFT JOIN voli ON a.id = voli.aeroportoArrivo LEFT JOIN pren_volo ON voli.id = pren_volo.id "+
					  "WHERE oli.dataOraArrivo <= %s"+
					  "GROUP BY a.nome) AS t2 "+
				"WHERE nomeA = nomeB", dataA, dataA).fetchall()

			infoVoli = conn.execute(
				"SELECT a1.nome, a2.nome, aerei.nome, pren_volo.pren/aerei.numeroPosti AS percentualeCarico, IFNULL(AVG(prenotazioni.valutazione),0) AS valutazioneMedia, voli.dataOraArrivo "+
				"FROM voli JOIN aeroporti AS a1 on voli.aeroportoPartenza = a1.id "+
						  "JOIN aeroporti AS a2 ON voli.aeroportoArrivo = a2.id "+
						  "JOIN aerei ON voli.aereo = aerei.id JOIN pren_volo ON voli.id = pren_volo.id "+
						  "LEFT JOIN prenotazioni on voli.id = prenotazioni.id_volo "+
				"WHERE voli.dataOraArrivo<= %s"+
				"GROUP BY voli.id HAVING voli.dataOraArrivo <= CURRENT_DATE", dataA).fetchall()
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
				"SELECT a1.nome, a2.nome, aerei.nome, pren_volo.pren/aerei.numeroPosti AS percentualeCarico, IFNULL(AVG(prenotazioni.valutazione),0) AS valutazioneMedia, voli.dataOraArrivo "+
				"FROM voli JOIN aeroporti AS a1 on voli.aeroportoPartenza = a1.id "+
						  "JOIN aeroporti AS a2 ON voli.aeroportoArrivo = a2.id "+
						  "JOIN aerei ON voli.aereo = aerei.id JOIN pren_volo ON voli.id = pren_volo.id "+
						  "LEFT JOIN prenotazioni on voli.id = prenotazioni.id_volo "+
				"WHERE voli.dataOraPartenza >= %s"+
				"GROUP BY voli.id HAVING voli.dataOraArrivo <= CURRENT_DATE",dataDa).fetchall()

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
				"SELECT a1.nome, a2.nome, aerei.nome, pren_volo.pren/aerei.numeroPosti AS percentualeCarico, IFNULL(AVG(prenotazioni.valutazione),0) AS valutazioneMedia, voli.dataOraArrivo "+
				"FROM voli JOIN aeroporti AS a1 on voli.aeroportoPartenza = a1.id "+
						  "JOIN aeroporti AS a2 ON voli.aeroportoArrivo = a2.id "+
						  "JOIN aerei ON voli.aereo = aerei.id JOIN pren_volo ON voli.id = pren_volo.id "+
						  "LEFT JOIN prenotazioni on voli.id = prenotazioni.id_volo "+
				"GROUP BY voli.id HAVING voli.dataOraArrivo <= CURRENT_DATE").fetchall()

	trattaGuadagniMax = conn.execute("SELECT IFNULL(aeroportoP, 'None'), IFNULL(aeroportoA, 'None'), IFNULL(guadagniTot,0) FROM guadagniTratte WHERE guadagniTot = (SELECT MAX(guadagniTot) FROM guadagniTratte)").fetchone()
	#CREATE OR REPLACE VIEW guadagniTratte AS SELECT a1.nome AS aeroportoP, a2.nome AS aeroportoA, SUM(voli.prezzo)+SUM(p.prezzo_bagaglio) AS guadagniTot FROM aeroporti AS a1 JOIN voli on a1.id = voli.aeroportoPartenza JOIN aeroporti AS a2 ON voli.aeroportoArrivo = a2.id JOIN prenotazioni AS p ON voli.id = p.id_volo GROUP BY a1.nome, a2.nome

	conn.close()
	return render_template('statistiche.html', title='Statistiche', fromStat = statisticsForm, totPasseggeri = totPasseggeri[0], totPasseggeriMese = totPasseggeri_mese[0], aeroporti = infoAeroporti, guadagniTot = guadagniTotali[0], trattaGuadagniMax = trattaGuadagniMax, voli=infoVoli)


#SELECT a1.nome, a2.nome, aerei.nome, pren_volo.pren/aerei.numeroPosti AS percentualeCarico, IFNULL(AVG(prenotazioni.valutazione), 'Nessuna recensione') AS valutazioneMedia, voli.dataOraArrivo FROM voli JOIN aeroporti AS a1 on voli.aeroportoPartenza = a1.id JOIN aeroporti AS a2 ON voli.aeroportoArrivo = a2.id JOIN aerei ON voli.aereo = aerei.id JOIN pren_volo ON voli.id = pren_volo.id LEFT JOIN prenotazioni on voli.id = prenotazioni.id_volo GROUP BY voli.id HAVING voli.dataOraArrivo <= CURRENT_DATE