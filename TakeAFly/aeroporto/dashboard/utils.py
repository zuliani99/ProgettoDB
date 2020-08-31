import secrets
from flask_mail import Message
from aeroporto import mail

def send_mail_deletefly(volo_id, usersmail_infovolo):
	msg = Message('Attenzione, volo ' + str(volo_id) + " CANCELLATO!", sender='takeaflyspa@gmail.com', recipients=[usersmail_infovolo[0]])
	msg.body = f'''Salve, ci scusiamo molto ma a causa di alcuni inconvenienti il volo da lei prenotato è satato cancellato.
Lo staff Take a Fly
'''
	mail.send(msg)
