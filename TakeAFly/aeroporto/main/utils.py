from functools import wraps
from flask_login import current_user
from aeroporto.table import load_user
from flask import url_for, redirect, flash

def login_required(role="ANY"):	# Override della funzione login_required
	def wrapper(fn):
		@wraps(fn)
		def wrap(*args, **kwargs):
			if not current_user.is_authenticated:	# Se l'utente non è autenticato
				flash("Devi accedere al tuo account per visitare la pagina", 'danger')
				return redirect(url_for('users.login'))
			urole = load_user(current_user.id).get_urole()
			if ((urole != role) and (role == "admin")): 	# Se il ruolo dell'utente e il ruolo richiesto per quella funzione sono diversi e il ruolo dell'utente è admin
				flash("Devi essere un admin per visualizzare la pagina", 'danger')
				return redirect(url_for('main.home'))
			elif ((urole != role) and (role == "customer")): # Se il ruolo dell'utente e il ruolo richiesto per quella funzione sono diversi e il ruolo dell'utente è customer
				flash("Devi essere un cliente per visualizzare la pagina", 'danger')
				return redirect(url_for('main.home'))
			return fn(*args, **kwargs)
		return wrap
	return wrapper