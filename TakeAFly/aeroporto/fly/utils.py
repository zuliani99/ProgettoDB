import secrets
from flask_mail import Message
from aeroporto import mail
from flask_login import current_user

# Funzione per l'invio della mail di prenotazione bgglietti/o
def send_ticket_notify(volopart, npostopart, bagpart, volorit, npostorit, bagrit):
	# Se non c'è il volo per il ritrono ho prenotato solo quello di andata
	if (volorit == 0):
		# Titolo e destinatari della mail
		msg = Message('Conferma di Acquisto Tiket: ' + str(volopart[0]), sender='takeaflyspa@gmail.com', recipients=[current_user.email])
		# Corpo della mail
		msg.body = f'''Grazie per aver acuistato dal nostro sito, ecco tutto ciò che ti serve per l'imbarco:

Dettagli volo
Codice Volo: {volopart[0] }
Aeroporto di Partenza: { volopart[1] }
Orario: { volopart[2] }
Aeroporto di Arrivo: { volopart[3] }
Orario: { volopart[4] }
Numero posto da sedere: {npostopart}
Tipologia di bagaglio: { bagpart[1] }
Costo totale: {volopart[5]+bagpart[0]}

Dettagli del cliente
Username: {current_user.username}
Email: {current_user.email}


Esibisci questo documento per il check-in

Vi auguriamo un bon viaggio
Lo staff Take a Fly

'''		# Invio effettivo della mail
		mail.send(msg)
	else:
		# Se  c'è il volo per il ritrono ho prenotato solo quello di andata e ritorno
		# Titolo e destinatari della mail
		msg = Message('Conferma di Acquisto Tiket: ' + str(volopart[0]) + " / " + str(volorit[0]), sender='akeaflyspa@gmail.com', recipients=[current_user.email])
		# Corpo della mail
		msg.body = f'''Grazie per aver acuistato dal nostro sito, ecco tutto ciò che ti serve per l'imbarco:

Dettagli del volo di ANDATA
Codice Volo: {volopart[0] }
Aeroporto di Partenza: { volopart[1] }
Orario: { volopart[2] }
Aeroporto di Arrivo: { volopart[3] }
Orario: { volopart[4] }
Numero posto da sedere: {npostopart}
Tipologia di bagaglio: { bagpart[1] }
Costo totale: {volopart[5]+bagpart[0]}

Dettagli del volo di RITRONO
Codice Volo: {volorit[0] }
Aeroporto di Partenza: { volorit[1] }
Orario: { volorit[2] }
Aeroporto di Arrivo: { volorit[3] }
Orario: { volorit[4] }
Numero posto da sedere: {npostorit}
Tipologia di bagaglio: { bagpart[1] }
Costo totale: {volorit[5]+bagrit[0]}

Dettagli del cliente
Username: {current_user.username}
Email: {current_user.email}


Esibisci questo documento per il check-in

Vi auguriamo un bon viaggio
Lo staff Take a Fly

'''		# Invio effettivo della mail
		mail.send(msg)


# Funzione per il calcolo dei posti disponibili per un dato volo
def get_available_sit(res, volo):
	temp = []
	# Utilizzo una lista d'appoggio temporanea per salvarmi i posti occupati in una lista
	for r in res:
		temp.append(r[0])
	# dichiaro la lista risultante
	available_sits = []
	# Itero per tutti i posti presenti nel volo
	for count in range(1,int(volo[6])+1):
		# Se quel posto non è nella mia lista di posti occupati
		if count not in temp:
			# Salvo quel posto nella mia lista risulatnte
			available_sits.append(count)
	# Converto i miei elemennti della lista in stringhe
	map(str(),available_sits)
	return available_sits
