import secrets
from flask_mail import Message
from aeroporto import mail

def send_ticket_notify(volopart, npostopart, bagpart, volorit, npostorit, bagrit):
	if (volorit == 0):
		msg = Message('Conferma di Acquisto Tiket: ' + str(volopart[0]), sender='takeaflyspa@gmail.com', recipients=[current_user.email])
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

'''
		mail.send(msg)
	else:
		msg = Message('Conferma di Acquisto Tiket: ' + str(volopart[0]) + " / " + str(volorit[0]), sender='akeaflyspa@gmail.com', recipients=[current_user.email])
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

'''
		mail.send(msg)



def get_available_sit(res, volo):
	temp = []
	for r in res:
		temp.append(r[0])
	available_sits = []
	for count in range(1,int(volo[6])+1):
		if count not in temp:
			available_sits.append(count)
	map(str(),available_sits)
	return available_sits
