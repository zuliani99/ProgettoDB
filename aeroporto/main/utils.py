from functools import wraps
from flask_login import current_user
from aeroporto.table import load_user
from flask import url_for, redirect, flash

def login_required(role="ANY"):
	def wrapper(fn):
		@wraps(fn)
		def wrap(*args, **kwargs):
			if not current_user.is_authenticated:
				flash("Devi accedere al tuo account per visitare la pagina", 'danger')
				return redirect(url_for('login'))
			urole = load_user(current_user.id).get_urole()
			if ((urole != role) and (role == "admin")):
				flash("Devi essere un admin per visualizzare la pagina", 'danger')
				return redirect(url_for('home'))
			elif ((urole != role) and (role == "customer")):
				flash("Devi essere un cliente per visualizzare la pagina", 'danger')
				return redirect(url_for('home'))
			return fn(*args, **kwargs)
		return wrap
	return wrapper