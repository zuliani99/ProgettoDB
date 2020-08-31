import secrets, os
from PIL import Image 
from flask import url_for
from flask_mail import Message
from aeroporto import app, mail

def save_pictures(form_picture): # Funzione di salvataggio dell'immagine di profilo nel filesystem
	random_hex = secrets.token_hex(8)   # Creazioen di una stringa random
	_, f_ext = os.path.splitext(form_picture.filename) # Prendiamo l'estensione del ifile
	picture_fn = random_hex + f_ext     # L'aggiungiamo alla stringa random
	picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn) # Salviamo il nuovo file nel filesystem
	
	output_size = (125, 125) # Impostiamo le dimensione che vogliamo avere dell'immagine
	i = Image.open(form_picture) # Apriamo l'immagine
	i.thumbnail(output_size) # Cambiamo le dimensioni
	i.save(picture_path) # La risalviamo
	
	return picture_fn


def send_reset_email(user):	 # Funzione per l'invio della mail per il password reset
	token = user.get_reset_token() # Prendiamo il token
	msg = Message('Richiesta di Password Reset', sender='takeaflyspa@gmail.com', recipients=[user.email]) # Titolo e destinatario del messaggio
	msg.body = f'''Per resettare la password, visita il seguente link: # Corpo del messaggio
{url_for('users.reset_token', token=token, _external=True)}

Se non hai fatto questa richiesta, ignora questa mail e nessuna modifica sarà effettuata
''' 
	mail.send(msg) # Invio effettivo del messaggio