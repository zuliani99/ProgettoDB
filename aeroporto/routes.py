# -*- coding: utf-8 -*-
import secrets
import os
from PIL import Image #pip install Pillow
from flask import render_template, url_for, flash, redirect, request, abort, current_app #import necessari per il funzionamento dell'applicazione
from aeroporto import app, bcrypt, mail
from aeroporto.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, AddBookingGone, AddBookingReturn, PlaneForm,  AirportForm, AddReviw, SearchFlyForm, FlightForm
from flask_login import login_user, current_user, logout_user
from aeroporto.table import User, users, engine, metadata, load_user, voli, aerei, aeroporti, deleteElementByID
from flask_mail import Message
from sqlalchemy.sql import *
from functools import wraps
from flask_principal import identity_changed, Identity, AnonymousIdentity
from flask_mysqldb import MySQL
from datetime import datetime, date, timedelta

def login_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def wrap(*args, **kwargs):
            if not current_user.is_authenticated:
                #return current_app.login_manager.unauthorized()
                flash("Devi accedere al tuo account per visitare la pagina", 'danger')
                return redirect(url_for('login'))
            urole = load_user(current_user.id).get_urole()
            if ((urole != role) and (role != "ANY")):
                #return current_app.login_manager.unauthorized()
                flash("Devi essere un admin per visualizzare la pagina", 'danger')
                return redirect(url_for('home'))
            return fn(*args, **kwargs)
        return wrap
    return wrapper


@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
    searchForm = SearchFlyForm()

    andata=ritorno=[]
    is_return = False

    conn = engine.connect()
    aeroporti = conn.execute("SELECT id, name, indirizzo FROM aeroporti").fetchall()
        
    opzioniAeroporti = [(str(choice[0]), str(choice[1]+", "+choice[2])) for choice in aeroporti]
    searchForm.aeroportoPartenza.choices = [('','')] + opzioniAeroporti
    searchForm.aeroportoArrivo.choices = [('','')] + opzioniAeroporti

    if searchForm.validate_on_submit():
        aPart = searchForm.aeroportoPartenza.data
        aArr = searchForm.aeroportoArrivo.data
        dPart = searchForm.dataPartenza.data
        dRit = searchForm.dataRitorno.data
        is_return = searchForm.checkAndataRitorno.data

        print(str(aPart) + " " + str(dPart)  + " " + str(aArr) + " " + str(dRit) + " " + str(is_return))
        queryandata = "SELECT v.id , part.name, v.oraPartenza, arr.name, v.oraArrivo, v.prezzo FROM voli v, aeroporti arr, aeroporti part, aerei a WHERE v.aeroportoArrivo = arr.id AND v.aeroportoPartenza = part.id AND v.aereo = a.id AND part.id = "+str(aPart)+" AND arr.id = "+str(aArr)+" AND v.oraPartenza BETWEEN '"+str(dPart)+" 00:00:00' AND '"+str(dPart)+" 23:59:59'"
        #print(query)
        andata = conn.execute(queryandata).fetchall()

        if dRit is not None:
            queryritorno = "SELECT v.id , part.name, v.oraPartenza, arr.name, v.oraArrivo, v.prezzo FROM voli v, aeroporti arr, aeroporti part, aerei a WHERE v.aeroportoArrivo = arr.id AND v.aeroportoPartenza = part.id AND v.aereo = a.id AND part.id = "+str(aArr)+" AND arr.id = "+str(aPart)+" AND v.oraPartenza BETWEEN '"+str(dRit)+" 00:00:00' AND '"+str(dRit)+" 23:59:59'"
            ritorno = conn.execute(queryritorno).fetchall()


    else:
        andata = conn.execute("SELECT v.id , part.name, v.oraPartenza, arr.name, v.oraArrivo, v.prezzo FROM voli v, aeroporti arr, aeroporti part, aerei a WHERE v.aeroportoArrivo = arr.id and v.aeroportoPartenza = part.id and v.aereo = a.id and v.oraPartenza > %s ORDER BY v.oraPartenza ASC", datetime.utcnow()).fetchall()
        
    #print(str(is_return))
    conn.close()
    return render_template('home.html', voliand=andata, volirit=ritorno, flyForm=searchForm, is_return=is_return)
    #, page=page, mp=math.ceil(m[0]/5))

@app.route("/about") #mi renderizza il template about.html con variabuile title='About'
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST']) #metodo reguister, in cui dal file form.py inizializza un nuovo RegistrationForm(),
def register():
    if current_user.is_authenticated: 
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit(): #controlla che tutte le regole del form siano state passate con successo
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') # criptiamo la password

        conn = engine.connect()
        conn.execute(users.insert(),[{"username": form.username.data, "email": form.email.data, "password": hashed_password}])
        conn.close()


        flash('Il tuo account è stato creato! Ora puoi effettuare il log in', 'success') # messaggio di avvenuto sing up al blog
        return redirect(url_for('login')) # redirect alla funzione home
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])  # metodo per la fase di login, in cui da form.py inizializza un nuovo loginform
def login():
    if current_user.is_authenticated: 
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit(): #controlla che tutte le regole del form siano state passate con successo
        
        conn = engine.connect()
        rs = conn.execute(select([users]).where(users.c.email == form.email.data))
        u = rs.fetchone()
        conn.close()
        if u is not None:
            user = User(u.id, u.username, u.email, u.image_file, u.password, u.role)

            if user and bcrypt.check_password_hash(user.password, form.password.data): 
                login_user(user, remember=form.remember.data) 
                identity_changed.send(current_app._get_current_object(), identity=Identity(user.role))
                next_page = request.args.get('next') # se prima di accedere ho provato ad enbtrarte nella pagina account mi salvo i paramentri del url
                return redirect(next_page) if next_page else redirect(url_for('home')) # e ritorno a quella pagina altrimenti mi ritorna alla homepage
    
        flash('Login non riuscito. Controlla elìmail e password', 'danger') # messaggio di login incorretta
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout(): # funzuione di logout
    logout_user()
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
    return redirect(url_for('home')) # mi riporta alla homepage

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


@app.route("/account", methods=['GET', 'POST'])
@login_required(role="ANY") # necessario se vogliaomo ch la pagina sia visitabile solo se l'utente ha eseguito l'accesso alla piattaforma
def account(): # funzione di account
    form = UpdateAccountForm()  # from di updaTE
    if form.validate_on_submit():  # se abbiamo cliccato aggiorna profilo
        if form.picture.data: # se abbiao aggiornato l'immagine
            picture_file = save_pictures(form.picture.data)
            current_user.image_file = picture_file
            
            conn = engine.connect()
            conn.execute(users.update().values(image_file=current_user.image_file).where(users.c.id==current_user.id))
            conn.close()


        current_user.username = form.username.data
        current_user.email = form.email.data
        

        conn = engine.connect()
        u = users.update().values(username=current_user.username, email=current_user.email).where(users.c.id==current_user.id)
        conn.execute(u)
        conn.close()

        flash('Il tuo account è stato aggionato', 'success')
        return redirect(url_for('account')) # non facciamo il render template, perchè altrienti il browser capirebbe che andremmo a fare un'altra post request
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form) # mi porta alla pagina accout con titolo='Account'



#funzione per inviare le mail
def send_reset_email(user):
    token = user.get_reset_token() #prendiamo il token
    msg = Message('PRichiesta di Password Reset', sender='noreplay@demo.com', recipients=[user.email]) #header del messaggio
    msg.body = f'''Per resettare la password, visita il seguente link: 
{url_for('reset_token', token=token, _external=True)}

Se non hai fatto questa richiesta, ignora questa mail e nessuna modifica sarà effettuata
''' #body del messaggio
    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST']) #route per inserire la mail per il recuper della password
def reset_request():
    if current_user.is_authenticated: 
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():

        conn = engine.connect()
        rs = conn.execute(select([users]).where(users.c.email == form.email.data))
        u = rs.fetchone()
        conn.close()
        user = User(u.id, u.nome, u.email, u.image_file, u.password, u.role)

        send_reset_email(user)  # la inviamo
        flash('Una mial ti è stata inviata con le istruzioni per resettare la password', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated: 
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None: # se il token non è valido
        flash('TTOken invalido o scaduto', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm() # altrimenti prendiamo la form per il reset della password
    if form.validate_on_submit(): #controlla che tutte le regole del form siano state passate con successo
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') # criptiamo la password
        user.password = hashed_password
        
        #db.session.commit() # e committiamo 
        conn = engine.connect()
        conn.execute(users.update().values(password=user.password).where(users.c.id==user.id))
        conn.close()

        flash('La tua password  stata aggiornata! Ora puoi eseguire il log in', 'success')
        return redirect(url_for('login')) # redirect alla funzione login
    return render_template('reset_token.html', title='Reset Password', form=form)


def send_ticket_notify(volopart, npostopart, bagpart, volorit, npostorit, bagrit):
    if (volorit == 0):
        msg = Message('Conferma di Acquisto Tiket: ' + str(volopart[0]), sender='akeaflyspa@gmail.com', recipients=[current_user.email])
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

@app.route("/volo<volopart>", methods=['GET', 'POST'])
def volo(volopart):
    form = AddBookingGone()
    conn = engine.connect()
    trans = conn.begin()
    try:
        conn.execute("CREATE VIEW pren_volo AS SELECT v.id, count(p.id) AS pren FROM voli v LEFT JOIN prenotazioni p ON v.id = p.id_volo GROUP BY v.id")
    except:
        trans.rollback()
    volo = conn.execute("SELECT v.id , part.name, v.oraPartenza, arr.name, v.oraArrivo, v.prezzo, a.numeroPosti, a.numeroPosti-pv.pren as postdisp FROM voli v, aeroporti arr, aeroporti part, aerei a, pren_volo pv WHERE v.aeroportoArrivo = arr.id and v.aeroportoPartenza = part.id and v.aereo = a.id and pv.id = v.id and v.id = %s",volopart).fetchone()
    #print("SELECT v.id , part.name, v.oraPartenza, arr.name, v.oraArrivo, v.prezzo, a.numeroPosti, a.numeroPosti-pv.pren as postdisp FROM voli v, aeroporti arr, aeroporti part, aerei a, pren_volo pv WHERE v.aeroportoArrivo = arr.id and v.aeroportoPartenza = part.id and v.aereo = a.id and pv.id = v.id and v.id = "+volopart)
    pocc = conn.execute("SELECT p.numeroPosto FROM voli v JOIN prenotazioni p ON v.id = p.id_volo WHERE v.id = %s",volopart).fetchall()
    conn.close()
    
    l = []
    for p in pocc:
        l.append(p[0])
    available_groups = []
    for count in range(1,int(volo[6])+1):
        if count not in l:
            available_groups.append(count)
    map(str(),available_groups)

    conn = engine.connect()

    res = conn.execute("SELECT prezzo, descrizione FROM bagagli").fetchall()
    form.bagaglioAndata.choices = [(str(r[0]), str(r[1])) for r in res]
    conn.close()

    if form.validate_on_submit():
        if current_user.is_authenticated:
            conn = engine.connect()
            r = conn.execute("SELECT * FROM prenotazioni WHERE id_volo = %s AND numeroPosto = %s", volopart, form.postoAndata.data).fetchone()
            if r is None:
                conn.execute("INSERT INTO prenotazioni (id_user, id_volo, numeroPosto, prezzo_bagaglio) VALUES (%s, %s, %s, %s)", current_user.id, volopart, form.postoAndata.data, form.bagaglioAndata.data)
                print("INSERT INTO prenotazioni (id_user, id_volo, numeroPosto, prezzo_bagaglio) VALUES ( "+str(current_user.id)+","+ str(volo[0])+","+ form.postoAndata.data+","+ form.bagaglioAndata.data+")")
                bagAndata = conn.execute("SELECT * FROM bagagli WHERE prezzo = %s", form.bagaglioAndata.data).fetchone()
                
                send_ticket_notify(volo, form.postoAndata.data, bagAndata, 0, 0, 0)
                
                flash('Acquisto completato. Ti abbiamo inviato una mail con tutte le informazioni del biglietto', 'success')
                return redirect(url_for('user_fly'))
                #possiamo modificare la tabella escludendo la prima select ed aggiungendo le transazioni
            else:
                flash("Posto da sedere appena acquistato, scegliene un altro", 'warning')
            conn.close()
        else:
            flash("Devi accedere al tuo account per acquistare il biglietto", 'danger')
            return redirect(url_for('login'))
    return render_template('volo.html', title=volopart, volo=volo, form=form, free=available_groups)


@app.route("/voli/<volopart>/<volorit>", methods=['GET', 'POST'])
def voli(volopart, volorit):
    form = AddBookingReturn()
    #olopart = request.args.get('volopart',1,type=int)
    #volorit = request.args.get('volorit',1,type=int)
    conn = engine.connect()
    trans = conn.begin()
    try:
        conn.execute("CREATE VIEW pren_volo AS SELECT v.id, count(p.id) AS pren FROM voli v LEFT JOIN prenotazioni p ON v.id = p.id_volo GROUP BY v.id")
    except:
        trans.rollback()
    andata = conn.execute("SELECT v.id , part.name, v.oraPartenza, arr.name, v.oraArrivo, v.prezzo, a.numeroPosti, a.numeroPosti-pv.pren as postdisp FROM voli v, aeroporti arr, aeroporti part, aerei a, pren_volo pv WHERE v.aeroportoArrivo = arr.id and v.aeroportoPartenza = part.id and v.aereo = a.id and pv.id = v.id and v.id = %s",volopart).fetchone()
    #print("SELECT v.id , part.name, v.oraPartenza, arr.name, v.oraArrivo, v.prezzo, a.numeroPosti, a.numeroPosti-pv.pren as postdisp FROM voli v, aeroporti arr, aeroporti part, aerei a, pren_volo pv WHERE v.aeroportoArrivo = arr.id and v.aeroportoPartenza = part.id and v.aereo = a.id and pv.id = v.id and v.id = "+volopart)
    poccandata = conn.execute("SELECT p.numeroPosto FROM voli v JOIN prenotazioni p ON v.id = p.id_volo WHERE v.id = %s",volopart).fetchall()
    
    l = []
    for p in poccandata:
        l.append(p[0])
    available_groups_gone = []
    for count in range(1,int(andata[6])+1):
        if count not in l:
            available_groups_gone.append(count)
    map(str(),available_groups_gone)



    ritorno = conn.execute("SELECT v.id , part.name, v.oraPartenza, arr.name, v.oraArrivo, v.prezzo, a.numeroPosti, a.numeroPosti-pv.pren as postdisp FROM voli v, aeroporti arr, aeroporti part, aerei a, pren_volo pv WHERE v.aeroportoArrivo = arr.id and v.aeroportoPartenza = part.id and v.aereo = a.id and pv.id = v.id and v.id = %s",volorit).fetchone()
    poccritorno = conn.execute("SELECT p.numeroPosto FROM voli v JOIN prenotazioni p ON v.id = p.id_volo WHERE v.id = %s",volorit).fetchall()
    

    l = []
    for p in poccritorno:
        l.append(p[0])
    available_groups_return = []
    for count in range(1,int(ritorno[6])+1):
        if count not in l:
            available_groups_return.append(count)
    map(str(),available_groups_return)



    res = conn.execute("SELECT prezzo, descrizione FROM bagagli").fetchall()
    form.bagaglioAndata.choices = [(str(r[0]), str(r[1])) for r in res]
    form.bagaglioRitorno.choices = [(str(r[0]), str(r[1])) for r in res]
    conn.close()

    if form.validate_on_submit():
        if current_user.is_authenticated:
            conn = engine.connect()
            r1 = conn.execute("SELECT * FROM prenotazioni WHERE id_volo = %s AND numeroPosto = %s", volopart, form.postoAndata.data).fetchone()
            r2 = conn.execute("SELECT * FROM prenotazioni WHERE id_volo = %s AND numeroPosto = %s", volorit, form.postoRitorno.data).fetchone()
            if r1 is None and r2 is None:
                conn.execute("INSERT INTO prenotazioni (id_user, id_volo, numeroPosto, prezzo_bagaglio) VALUES (%s, %s, %s, %s)", current_user.id, andata[0], form.postoAndata.data, form.bagaglioAndata.data)
                conn.execute("INSERT INTO prenotazioni (id_user, id_volo, numeroPosto, prezzo_bagaglio) VALUES (%s, %s, %s, %s)", current_user.id, ritorno[0], form.postoRitorno.data, form.bagaglioRitorno.data)
                print("INSERT INTO prenotazioni (id_user, id_volo, numeroPosto, prezzo_bagaglio) VALUES ( "+str(current_user.id)+","+ str(andata[0])+","+ form.postoAndata.data+","+ form.bagaglioAndata.data+")")
                print("INSERT INTO prenotazioni (id_user, id_volo, numeroPosto, prezzo_bagaglio) VALUES ( "+str(current_user.id)+","+ str(ritorno[0])+","+ form.postoRitorno.data+","+ form.bagaglioRitorno.data+")")
                bagAndata = conn.execute("SELECT * FROM bagagli WHERE prezzo = %s", form.bagaglioAndata.data).fetchone()
                bagRitorno = conn.execute("SELECT * FROM bagagli WHERE prezzo = %s", form.bagaglioRitorno.data).fetchone()
                
                send_ticket_notify(andata, form.postoAndata.data, bagAndata, ritorno, form.postoRitorno.data, bagRitorno)
                
                flash('Acquisto completato. Ti abbiamo inviato una mail con tutte le informazioni del biglietto', 'success')
                return redirect(url_for('user_fly'))
                #possiamo modificare la tabella escludendo la prima select ed aggiungendo le transazioni
            else:
                if r1 is not None:
                    flash("Posto da sedere per l'andata appena acquistato, scegliene un altro", 'warning')
                if r2 is not None:
                    flash("Posto da sedere per il ritorno appena acquistato, scegliene un altro", 'warning')
            conn.close()
        else:
            flash("Devi accedere al tuo account per acquistare il biglietto", 'danger')
            return redirect(url_for('login'))
    return render_template('voli.html', title=volopart + volorit, volopart=andata, volorit=ritorno, form=form, freegone=available_groups_gone, freereturn=available_groups_return)


@app.route("/user_fly", methods=['GET', 'POST'])
@login_required(role="customer")
def user_fly():
    form = AddReviw()
    conn = engine.connect()
    voli = conn.execute("SELECT p.id, p.id_volo, v.aeroportoPartenza, v.oraPartenza, v.aeroportoArrivo, v.oraArrivo, v.aereo, p.numeroPosto, v.prezzo AS pstandard,  p.prezzo_bagaglio AS pbagaglio, b.descrizione, v.prezzo+p.prezzo_bagaglio AS ptotale, p.valutazione FROM prenotazioni p JOIN voli v ON p.id_volo = v.id JOIN bagagli b ON p.prezzo_bagaglio=b.prezzo WHERE p.id_user= %s ORDER BY v.oraPartenza", current_user.id).fetchall()
    conn.close()
    time = datetime.now()
    if form.validate_on_submit():
        return redirect(url_for('review_fly', fly_id=form.idnascosto.data, val=form.valutazione.data, crit=form.critiche.data))
    return render_template('imieivoli.html', voli=voli, time=time, form=form)
    



@app.route("/delete_fly<int:fly_id>", methods=['GET', 'POST'])
@login_required(role="customer")
def delete_fly(fly_id):
    conn = engine.connect()
    f = conn.execute("SELECT * FROM prenotazioni WHERE id = %s",fly_id).fetchone()
    if f is None:
        abort(404)
    if f[1] != current_user.id:
        abort(403)
   
    conn.execute("DELETE FROM prenotazioni WHERE id = %s", fly_id)
    flash('Il volo ' + str(f[0]) + ' da te prenotato è stato cancellato con successo', 'success')
    conn.close()
    return redirect(url_for('user_fly'))





@app.route("/review_fly<fly_id>,<val>,<crit>", methods=['GET', 'POST'])
@login_required(role="customer")
def review_fly(fly_id, val, crit):
    conn = engine.connect()
    f = conn.execute("SELECT * FROM prenotazioni WHERE id = %s",fly_id).fetchone()
    if f is None:
        abort(404)
    if f[1] != current_user.id:
        abort(403)

    r = conn.execute("SELECT valutazione FROM prenotazioni WHERE id = %s", fly_id).fetchone()
    if r[0] is None: 
        conn.execute("UPDATE prenotazioni SET valutazione = %s , critiche = %s WHERE id = %s", val, crit, fly_id)
        conn.close()
        flash("Recensione inserita con successo", "success")
    else:
        flash("Recensione già inserita con successo", "warning")
    return redirect(url_for('user_fly'))




#DASHBOARD

@app.route("/delete_volo<int:volo_id>", methods=['GET', 'POST'])
@login_required(role="admin")
def delete_volo(volo_id):

    result = deleteElementByID("id", volo_id, "voli")
    if result:
        flash('Il volo ' + str(volo_id) + ' è stato cancellato con successo', 'success')

    return redirect(url_for('dashboard'))

@app.route("/delete_aeroporto<int:aeroporto_id>", methods=['GET', 'POST'])
@login_required(role="admin")

def delete_aeroporto(aeroporto_id):
    
    result = deleteElementByID("id", aeroporto_id, "aeroporti")
    if result:
        flash('l\'aeroporto ' + str(aeroporto_id) + ' è stato cancellato con successo', 'success')
        
    return redirect(url_for('dashboard'))

@app.route("/delete_aereo<int:aereo_id>", methods=['GET','POST'])
@login_required(role="admin")
def delete_aereo(aereo_id):

    result = deleteElementByID("id", aereo_id, "aerei")
    if result:
        flash('l \'aereo ' + str(aereo_id) + ' è stato cancellato con successo', 'success')
    
    return redirect(url_for('dashboard'))

@app.route("/dashboard", methods=['GET', 'POST'])
@login_required(role="admin")
def dashboard():
	flyForm = AddFlyForm()
	planeForm = PlaneForm()
	airportForm = AirportForm()

    conn = engine.connect()
    aeroporti = conn.execute("SELECT id, name, indirizzo FROM aeroporti").fetchall()
    aerei = conn.execute("SELECT id, name, numeroPosti FROM aerei").fetchall()
    voli = conn.execute("SELECT * FROM voli").fetchall()
    conn.close()

	opzioniAeroporti = [(str(choice[0]), str(choice[1]+", "+choice[2]+" #"+str(choice[0]))) for choice in aeroporti]
	flyForm.aeroportoPartenza.choices = [('','')] + opzioniAeroporti
	flyForm.aeroportoArrivo.choices = [('','')] + opzioniAeroporti

	opzioniAerei = [(str(choice[0]), str(choice[1]+" #"+str(choice[0]))) for choice in aerei]
	flyForm.aereo.choices = [('','')]  + opzioniAerei
	
	time = datetime.now()

	flightForm.check = False;

	if flyForm.is_submitted() and flyForm.submitFly.data:
		if flyForm.validate():
			oraPartenza = datetime.combine(flyForm.dataPartenza.data, flyForm.oraPartenza.data)
			if flyForm.oraPartenza.data > flyForm.oraArrivo.data:
				oraArrivo = datetime.combine(flyForm.dataPartenza.data + timedelta(days=1), flyForm.oraArrivo.data)
			else:
				oraArrivo = datetime.combine(flyForm.dataPartenza.data, flyForm.oraArrivo.data)

			conn = engine.connect()
			#conn.execute(voli.insert(),[{"aeroportoPartenza": flyForm.aeroportoPartenza.data,"oraPartenza": oraPartenza,"aeroportoArrivo": flyForm.aeroportoArrivo.data,"oraArrivo": oraArrivo,"aereo": flyForm.aereo.data,"prezzo": flyForm.prezzo.data}])
			conn.execute("INSERT INTO voli (aeroportoPartenza, oraPartenza, aeroportoArrivo, oraArrivo, aereo,prezzo) VALUES (%s,%s,%s,%s,%s,%s)", 
				flyForm.aeroportoPartenza.data, 
				oraPartenza, 
				flyForm.aeroportoArrivo.data, 
				oraArrivo, 
				flyForm.aereo.data,
				flyForm.prezzo.data
			)
			conn.close()
		   
			flash('Aggiunta volo completata con successo :D', 'success')
			return redirect('dashboard')
		else:
			flash('Qualcosa nell\'inserimento del volo è andato storto :(', 'danger')
	
	if planeForm.is_submitted() and planeForm.submitPlane.data:
		if planeForm.validate():
			conn = engine.connect()
			conn.execute("INSERT INTO aerei (name, numeroPosti) VALUES (%s, %s)", planeForm.nome.data, planeForm.nPosti.data)

            #se si usa questa linea: typeerror insert() takes exactly 2 arguments (0 given) python mysql
            #conn.execute(aerei.insert(),[{"name": planeForm.nome.data, "numeroPosti": planeForm.nPosti.data}])

            conn.close()

            flash('Aggiunta aereo completata con successo :)', 'success')
            return redirect('dashboard')
        else:
            flash('Qualcosa nell\'inserimento dell\'aereo è andato storto :(', 'danger')
    
    if airportForm.is_submitted() and airportForm.submitAirport.data:
        if airportForm.validate():
            conn = engine.connect()
            conn.execute("INSERT INTO aeroporti (name, indirizzo) VALUES (%s, %s)", airportForm.nome.data, airportForm.indirizzo.data)

            #conn.execute(aeroporti.insert(),[{"name": airportForm.nome.data, "indirizzo": airportForm.indirizzo.data}])
            conn.close()

            flash('Aggiunta aeroporto completata con successo :D', 'success')
            return redirect('dashboard')
        else:
            flash('Qualcosa nell\'inserimento dell\'aeroporto è andato storto :(', 'danger')

	return render_template('dashboard.html', title='Dashboard', flyForm=flyForm, planeForm=planeForm, airportForm=airportForm, voli=voli, aeroporti=aeroporti, aerei=aerei,time=time)


@app.route("/dashboard_volo<volo_id>", methods=['GET', 'POST'])
@login_required(role="admin") 
def configVolo(volo_id): 
	updateform = UpdateFlyForm() 

    conn = engine.connect()
    volo = conn.execute("SELECT id, aeroportoPartenza, oraPartenza, aeroportoArrivo, oraArrivo, aereo, prezzo FROM voli WHERE id=%s", volo_id).fetchone()
    aeroporti = conn.execute("SELECT id, name, indirizzo FROM aeroporti").fetchall()
    aerei = conn.execute("SELECT id, name FROM aerei").fetchall()
    voli = conn.execute("SELECT * FROM voli").fetchall()
    conn.close()

	opzioniAeroporti = [(str(choice[0]), str(choice[1]+", "+choice[2]+" #"+str(choice[0]))) for choice in aeroporti]
	updateform.aeroportoPartenza.choices = [('','')] + opzioniAeroporti
	updateform.aeroportoArrivo.choices = [('','')] + opzioniAeroporti


	opzioniAerei = [(str(choice[0]), str(choice[1]+" #"+str(choice[0]))) for choice in aerei]
	updateform.aereo.choices = [('','')]  + opzioniAerei

	#Set the informations of the fly in each field 
	if updateform.validate_on_submit():
		conn = engine.connect()
		
		conn.execute("UPDATE voli SET aeroportoPartenza=%s, oraPartenza=%s,aeroportoArrivo=%s,oraArrivo=%s,aereo=%s,prezzo=%s WHERE id = %s", 
			updateform.aeroportoPartenza.data,
			updateform.timePartenza.data,
			updateform.aeroportoArrivo.data,
			updateform.timeArrivo.data,
			updateform.aereo.data,
			updateform.prezzo.data,
			volo_id
		)
		conn.close()
		flash('Aggiornamento volo completato con successo :D', 'success')
		return redirect('dashboard')
	elif request.method == 'GET':
		updateform.aeroportoPartenza.data = str(volo[1])
		updateform.timePartenza.data = volo[2]
		updateform.aeroportoArrivo.data = str(volo[3])
		updateform.timeArrivo.data = volo[4]
		updateform.aereo.data = str(volo[5])
		updateform.prezzo.data = volo[6]
		
	return render_template('dashboard_volo.html', volo=volo, flyForm=updateform)

@app.route("/dashboard_aeroporto<aeroporto_id>", methods=['GET', 'POST'])
@login_required(role="admin")
def configAeroporto(aeroporto_id):
    updateform = AirportForm()

    conn = engine.connect()
    aeroporto = conn.execute("SELECT id, name, indirizzo FROM aeroporti WHERE id = %s", aeroporto_id).fetchone()
    conn.close()

    if updateform.validate_on_submit():
        conn = engine.connect()
        conn.execute("UPDATE aeroporti SET name=%s, indirizzo=%s WHERE id = %s",
            updateform.nome.data,
            updateform.indirizzo.data,
            aeroporto_id
        )
        conn.close()
        flash('Aggiornamento aeroporto completato con successo :D', 'success')
        return redirect('dashboard')
    elif request.method == 'GET':
        updateform.nome.data = aeroporto[1]
        updateform.indirizzo.data = aeroporto[2]
        #updateform.submitAirport.label = "Aggiorna"

    return render_template('dashboard_aeroporto.html', aeroporto=aeroporto, airportForm=updateform)

@app.route("/dashboard_aereo<aereo_id>", methods=['GET', 'POST'])
@login_required(role="admin")
def configAereo(aereo_id):
    updateform = PlaneForm()

    conn = engine.connect()
    aereo = conn.execute("SELECT id, name, numeroPosti FROM aerei WHERE id = %s", aereo_id).fetchone()
    conn.close()

    if updateform.validate_on_submit():
        conn = engine.connect()
        conn.execute("UPDATE aerei SET name=%s, numeroPosti=%s WHERE id = %s",
            updateform.nome.data,
            updateform.nPosti.data,
            aereo_id
        )
        conn.close()
        flash('Aggiornamento aereo completato con successo :D', 'success')
        return redirect('dashboard')
    elif request.method == 'GET':
        updateform.nome.data = aereo[1]
        updateform.nPosti.data = aereo[2]
        #updateform.submitAirport.label = "Aggiorna"

    return render_template('dashboard_aereo.html', aereo=aereo, planeForm=updateform)

