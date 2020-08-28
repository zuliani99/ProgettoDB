from aeroporto import login_manager, app
from flask_login import UserMixin
from flask_user import current_user, roles_required, UserManager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy import *

from flask_mysqldb import MySQL


engine = create_engine('mysql://admin:admin@localhost')

engine.execute("CREATE DATABASE IF NOT EXISTS takeafly")

engine.execute("USE takeafly")

metadata = MetaData()

users = Table('users', metadata,
	Column('id', Integer, primary_key=True),
	Column('username', String(20), unique=True, nullable=False),
	Column('email', String(120), unique=True, nullable=False),
	Column('image_file', String(20), nullable=False, server_default='default.jpg'),
	Column('password', String(60), nullable=False),
	Column('role', String(10), nullable=False, server_default='customer')
)

aerei = Table('aerei', metadata,
	Column('id', Integer, primary_key=True),
	Column('nome', String(20), nullable=False, default='Boeing 777'),
	Column('numeroPosti', Integer, nullable=False, default=50),
	CheckConstraint('numeroPosti > 0', name='c_nposti')
)

aeroporti = Table('aeroporti', metadata,
	Column('id', Integer, primary_key=True),
	Column('nome', String(30), nullable = False),
	Column('indirizzo', String(60), nullable= False)
)

voli = Table('voli', metadata,
	Column('id', Integer, primary_key = True),
	Column('aeroportoPartenza', Integer, ForeignKey('aeroporti.id', ondelete="CASCADE"), nullable=False),
	Column('dataOraPartenza', DateTime, nullable=False),
	Column('aeroportoArrivo', Integer, ForeignKey('aeroporti.id', ondelete="CASCADE"), nullable=False),
	Column('dataOraArrivo', DateTime, nullable=False),
	Column('aereo', Integer, ForeignKey('aerei.id', ondelete="CASCADE"),nullable=False),
	Column('prezzo', Float, nullable=False),
	CheckConstraint('prezzo > 0', name='c_prezzo'),
	CheckConstraint('dataOraArrivo > dataOraPartenza', name='c_date')
)

bagagli = Table('bagagli', metadata,
	Column('prezzo', Float, primary_key=True),
	Column('descrizione', String(60), nullable=False)
)

prenotazioni = Table('prenotazioni', metadata,
	Column('id', Integer, autoincrement = True, index = True),
	Column('id_user', Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False),
	Column('id_volo', Integer, ForeignKey('voli.id', ondelete="CASCADE"), nullable=False, primary_key = True),
	Column('prezzo_bagaglio', Float, ForeignKey('bagagli.prezzo'), nullable=False),
	Column('numeroPosto', Integer, nullable=False, primary_key = True),
	Column('valutazione', Integer, nullable=False, default=None),
	Column('critiche', String(200), nullable=False, default=None)
)

Index('idpren_index', prenotazioni.c.id)

metadata.create_all(engine)

from aeroporto import insert

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
	#s = conn.execute(select([users]).where(users.c.id == user_id)).fetchone()
	s = conn.execute("SELECT * FROM users WHERE id = %s", user_id).fetchone()
	conn.close()
	if s is None:
		return None
	return User(s.id, s.username, s.email, s.image_file, s.password, s.role)


def deleteElementByID(nameAttribute, idValue, nameTable):
	query = "SELECT * FROM "+nameTable+" WHERE "+nameAttribute+" = %s"
	conn = engine.connect()
	f = conn.execute(query, idValue).fetchone()
	if f is None:
		conn.close()
		abort(404)
		return False
	query = "DELETE FROM "+nameTable+" WHERE "+nameAttribute+" = %s"
	conn.execute(query, idValue)
	conn.close()
	return True