import secrets, os
from PIL import Image 
from flask import url_for
from flask_mail import Message
from aeroporto import app, mail

def save_pictures(form_picture): # funzione di salvataggio nel filesystem
	random_hex = secrets.token_hex(8)   #creazioen di una stringa random
	_, f_ext = os.path.splitext(form_picture.filename) # _ -> se non usaimao la variabile, ci prendiamo l'estensione del file
	picture_fn = random_hex + f_ext     #l'aggiungiamo alla stringa random
	picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn) # e salviamo il nuovo file nel filesystem
	
	output_size = (125, 125) # impostiamo le dimensione che vogliamo avere dell'immagine
	i = Image.open(form_picture) #apriamo l'immagine
	i.thumbnail(output_size) # cambiamo le dimensioni
	i.save(picture_path) # la risalviamo
	
	return picture_fn

#funzione per inviare le mail
def send_reset_email(user):
	token = user.get_reset_token() #prendiamo il token
	msg = Message('Richiesta di Password Reset', sender='takeaflyspa@gmail.com', recipients=[user.email]) #header del messaggio
	msg.body = f'''Per resettare la password, visita il seguente link: 
{url_for('reset_token', token=token, _external=True)}

Se non hai fatto questa richiesta, ignora questa mail e nessuna modifica sarà effettuata
''' #body del messaggio
	mail.send(msg)