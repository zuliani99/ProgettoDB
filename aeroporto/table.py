from aeroporto import login_manager, app
from flask_login import UserMixin
from flask_user import current_user, roles_required, UserManager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy import *

from aeroporto.routes import bcrypt
from flask_mysqldb import MySQL


engine = create_engine('mysql://admin:admin@localhost/MyDB')
metadata = MetaData()

users = Table('users', metadata,
	Column('id', Integer, primary_key=True),
	Column('username', String(20), unique=True, nullable=False),
	Column('email', String(120), unique=True, nullable=False),
	Column('image_file', String(20), nullable=False, default='default.jpg'),
	Column('password', String(60), nullable=False),
	Column('role', String(10), nullable=False, default='customer')
)

aerei = Table('aerei', metadata,
	Column('id', Integer, primary_key=True),
	Column('name', String(20), nullable=False, default='Boeing 777'),
	Column('numeroPosti', Integer, nullable=False, default=50)
)

aeroporti = Table('aeroporti', metadata,
	Column('id', Integer, primary_key=True),
	Column('name', String(20), nullable = False),
	Column('indirizzo', String(60), nullable= False)
)

voli = Table('voli', metadata,
	Column('id', Integer, primary_key = True),
	Column('aeroportoPartenza', Integer, ForeignKey('aeroporti.id'), nullable=False),
	Column('oraPartenza', DateTime, nullable=False),
	Column('aeroportoArrivo', Integer, ForeignKey('aeroporti.id'), nullable=False),
	Column('oraArrivo', DateTime, nullable=False),
	Column('aereo', Integer, ForeignKey('aerei.id'), nullable=False),
	Column('prezzo', Float, nullable=False)
)

bagagli = Table('bagagli', metadata,
	Column('prezzo', Float, primary_key=True),
	Column('descrizione', String(50), nullable=False)
)

prenotazioni = Table('prenotazioni', metadata,
	Column('id', Integer, primary_key = True),
	Column('id_user', Integer, ForeignKey('users.id'), nullable=False),
	Column('id_volo', Integer, ForeignKey('voli.id'), nullable=False),
	Column('prezzo_bagaglio', Integer, ForeignKey('bagagli.prezzo'), nullable=False),
	Column('numeroPosto', Integer, nullable=False),
	Column('valutazione', Integer, nullable=False, default=None),
	Column('critiche', String(200), nullable=True, default=None)
)

metadata.create_all(engine)


conn = engine.connect()
trans = conn.begin()
try:
	conn.execute("INSERT INTO users (username, email, image_file, password, role) VALUES ('Administrator', 'administrator@takeafly.com', 'default.jpg', %s, 'admin')",  bcrypt.generate_password_hash("adminpassword123").decode('utf-8'))
except:
	trans.rollback()

trans = conn.begin()
try:
	conn.execute("INSERT INTO aeroporti (name, indirizzo) VALUES ('Aeroporto di Roma', 'asc')")
	conn.execute("INSERT INTO aeroporti (name, indirizzo) VALUES ('Aeroporto di Milano', 'asc')")
	conn.execute("INSERT INTO aeroporti (name, indirizzo) VALUES ('Aeroporto di Treviso', 'asc')")
	conn.execute("INSERT INTO aeroporti (name, indirizzo) VALUES ('Aeroporto di Bologna', 'asc')")
	conn.execute("INSERT INTO aeroporti (name, indirizzo) VALUES ('Aeroporto di Firenze', 'asc')")
except:
	trans.rollback()

trans = conn.begin()
try:
	conn.execute("INSERT INTO aerei (numeroPosti) VALUES (50)")
	conn.execute("INSERT INTO aerei (numeroPosti) VALUES (60)")
	conn.execute("INSERT INTO aerei (numeroPosti) VALUES (100)")
except:
	trans.rollback()

trans = conn.begin()
try:
	conn.execute("INSERT INTO voli (aeroportoPartenza, oraPartenza, aeroportoArrivo, oraArrivo, aereo, prezzo) VALUES (3, '2020/08/31 14:00:00.000000', 1, '2020/08/31 15:00:00.000000', 1, 30)")
except:
	trans.rollback()

trans = conn.begin()
try:
	conn.execute("INSERT INTO bagagli (prezzo, descrizione) VALUES (0, 'Standard - Borsa piccola ( + 0€ )')")
	conn.execute("INSERT INTO bagagli (prezzo, descrizione) VALUES (20, 'Plus - Bagaglio a mano da 10 Kg e borsa piccola ( + 20€ )')")
	conn.execute("INSERT INTO bagagli (prezzo, descrizione) VALUES (40, 'Deluxe - Bagaglio a mano da 20Kg e borsa piccola ( + 40€ )'")
except:
	trans.rollback()

conn.close()


















class User(UserMixin):
    def __init__(self, id, username, email, image_file, password, role):
        self.id = id
        self.username = username
        self.email = email
        self.image_file = image_file
        self.password = password
        self.role = role

    def get_id(self):
        return self.id       
    def get_username(self):
        return self.username
    def get_email(self):
    	return self.email
    def get_password(self):
        return self.password
    def get_urole(self):
        return self.role

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')


    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return load_user(user_id)

    def __repr__(self):
        return "User('{self.nome}', '{self.email}', '{self.image_file}')"



@login_manager.user_loader
def load_user(user_id):
	conn = engine.connect()
	s = conn.execute(select([users]).where(users.c.id == user_id)).fetchone()
	conn.close()
	if s is None:
		return None
	return User(s.id, s.username, s.email, s.image_file, s.password, s.role)
