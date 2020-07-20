import sqlalchemy 
from sqlalchemy import *
# nuovo database transiente in RAM
from flask import Flask

engine = create_engine ('sqlite :// ', echo = True) # echo = True -> dubugging (di default è false)
metadata = MetaData()

users = Table ('users', metadata, #la tabella si chiama users, e va inserita in metadeta
    Column ('id', Integer, primary_key = True), #colonne che specificanpo iol tipo e i vincoli di integrità
    Column ('email', String),
    Column ('pwd', String)
) # andiamo a memorizzare 3 componeni per ogni utente

metadata.create_all(engine) # create_all crea tutte le entità che abbiamo definito di tipo table


conn = engine.connect() # apertura di una connessione verso l ’ engine
ins = users.insert() # INSERT INTO users ( name , fullname ) VALUES (? , ?)
conn.execute (ins, [ # dati da inserire nella tabella
    {"email": "riccardo.zuliani99@gmail.com", "pwd": "vivagesu99"},
    {"email": "antonio_zuliani@alice.it", "pwd": "nonlaso1963"},
    {"email": "ginomafioso@gmail.com", "pwd": "sfacimm11"}
])
conn.close()# chiusura della connessione

results = conn.execute(select([users]))

app = Flask(__name__)
@app.route('/')
def print_table():
    return 'ciao'