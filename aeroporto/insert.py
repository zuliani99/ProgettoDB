from aeroporto import bcrypt
from sqlalchemy import *

from aeroporto.table import engine

engine = create_engine('mysql://admin:admin@localhost/takeafly')
metadata = MetaData()
conn = engine.connect()

res = conn.execute("SELECT COUNT(*) FROM users").fetchone()
if res[0] == 0:
	conn.execute("INSERT INTO users (username, email, image_file, password, role) VALUES (%s, %s, %s, %s, %s), (%s, %s, %s, %s, %s), (%s, %s, %s, %s, %s)",
		'Administrator', 'administrator@takeafly.com', 'default.jpg', bcrypt.generate_password_hash("adminpassword123").decode('utf-8'), 'admin',
		'riccardo', 'riccardo.zuliani99@gmail.com', 'default.jpg', bcrypt.generate_password_hash("password").decode('utf-8'), 'customer',
		'michele', 'michelegatto@gmail.com', 'default.jpg', bcrypt.generate_password_hash("password2").decode('utf-8'), 'customer'
	)

res = conn.execute("SELECT COUNT(*) FROM aerei").fetchone()
if res[0] == 0:
	conn.execute("INSERT INTO aerei (nome, numeroPosti) VALUES (%s, %s), (%s, %s), (%s, %s), (%s, %s), (%s, %s)",
		'Boeing 742', 40,
		'Boeing 777', 60,
		'Boeing 142', 100,
		'Boeing 777', 100,
		'Boeing 222', 20
	)

res = conn.execute("SELECT COUNT(*) FROM aeroporti").fetchone()
if res[0] == 0:
	conn.execute("INSERT INTO aeroporti (nome, indirizzo) VALUES (%s, %s), (%s, %s), (%s, %s), (%s, %s), (%s, %s), (%s, %s), (%s, %s), (%s, %s)", 
		'Aeroporto di Treviso', 'Via Treviso 12',
		'Aeroporto di Milano', 'Via Milano 356',
		'Aeroporto di Venezia', 'Via Venezia 56',
		'Aeroporto di Roma', 'Via Roma 352',
		'Aeroporto di Firenze', ' Via Firenze 110',
		'Aeroporto di Praga', 'Via Praga Nord 123',
		'Aeroporto di Barcellona', 'Via Barcellona 12',
		'Aeroporto di Parigi', 'Via Parigi 56'
	)

res = conn.execute("SELECT COUNT(*) FROM voli").fetchone()
if res[0] == 0:
	conn.execute("INSERT INTO voli (aeroportoPartenza, dataOraPartenza, aeroportoArrivo, dataOraArrivo, aereo, prezzo) VALUES (%s, %s, %s, %s, %s, %s), (%s, %s, %s, %s, %s, %s), (%s, %s, %s, %s, %s, %s),(%s, %s, %s, %s, %s, %s), (%s, %s, %s, %s, %s, %s), (%s, %s, %s, %s, %s, %s) ",
			1, '2020-10-01 12:00:00', 2, '2020-10-01 12:30:00', 1, '40',
			3, '2020-09-02 10:00:00', 6, '2020-09-02 11:30:00', 2, '50',
			8, '2020-09-18 14:00:00', 6, '2020-09-18 16:00:00', 5, '100',
			6, '2020-09-09 18:00:00', 3, '2020-09-09 19:30:00', 3, '50',
			2, '2020-10-01 05:00:00', 7, '2020-10-01 07:00:00', 4, '60',
			7, '2020-10-08 10:00:00', 2, '2020-10-08 12:00:00', 4, '70'
		)

conn.execute("CREATE OR REPLACE VIEW pren_volo AS SELECT v.id, count(p.id) AS pren FROM voli v LEFT JOIN prenotazioni p ON v.id = p.id_volo GROUP BY v.id")

res = conn.execute("SELECT COUNT(*) FROM bagagli").fetchone()
if res[0] == 0:
	conn.execute("INSERT INTO bagagli (prezzo, descrizione) VALUES (%s, %s), (%s, %s), (%s, %s)",
		0, 'Standard - Borsa piccola ( + 0€ )',
		20, 'Plus - Bagaglio a mano da 10 Kg e borsa piccola ( + 20€ )',
		40, 'Deluxe - Bagaglio a mano da 20Kg e borsa piccola ( + 40€ )'
	)


conn.close()