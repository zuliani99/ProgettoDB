from aeroporto import login_manager, app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy import *
from datetime import datetime
from aeroporto.routes import bcrypt

engine = create_engine('sqlite:////tmp/test.db', echo=True)
metadata = MetaData()

users = Table('users', metadata,
	Column('id', Integer, primary_key=True),
	Column('name', String(20), unique=True, nullable=False),
	Column('email', String(120), unique=True, nullable=False),
	Column('image_file', String(20), nullable=False, default='default.jpg'),
	Column('password', String(60), nullable=False),
	Column('admin', Boolean, nullable=False, default=False)
)

aerei = Table('aerei', metadata,
	Column('id', Integer, primary_key=True),
	Column('numeroPosti', Integer, nullable=False, default=50)
)

aeroporti = Table('aeroporti', metadata,
	Column('id', Integer, primary_key=True),
	Column('name', String(20), nullable = False),
	Column('indirizzo', String(60), nullable= False)
)

voli = Table('voli', metadata,
	Column('id', Integer, primary_key = True),
	Column('aeropartoArrivo', Integer, ForeignKey('aeroporti.id'), nullable=False),
	Column('aeropartoPartenza', Integer, ForeignKey('aeroporti.id'), nullable=False),
	Column('aereo', Integer, ForeignKey('aerei.id'), nullable=False),
	Column('oraPartenza', DateTime, nullable=False),
	Column('oraArrivo', DateTime, nullable=False),
	Column('prezzo', Float, nullable=False)
)

prenotazioni = Table('prenotazioni', metadata,
	Column('id', Integer, primary_key = True),
	Column('id_user', Integer, ForeignKey('users.id'), nullable=False),
	Column('id_volo', Integer, ForeignKey('voli.id'), nullable=False),
	Column('numeroPosto', Integer, nullable=False)
)

role = Table ('role', metadata,
	Column('id', Integer, primary_key=True),
	Column('name', String(20), unique=True)
)

usersrole = Table('usersrole', metadata,
	Column('id', Integer, primary_key=True),
	Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
	Column('role_id', Integer, ForeignKey('role.id', ondelete='CASCADE'), nullable=False)
)

metadata.create_all(engine)
conn = engine.connect()
ins = role.insert()
conn.execute(ins, [
	{"name": "Admin"}, {"name": "Customer"}
])

ins = user.insert()
conn.execute(ins, [
	{"name": "Administrator", "email": "administrator@airport.com", "password": bcrypt.generate_password_hash("adminpassword123").decode('utf-8')}
])

result = conn.execute(select([users.c.id]).where(users.c.name == "Administrator")).fetchone()
ins = usersrole.insert()
conn.execute(ins, [
	{"user_id": result[0], "role_id": 1}
])

conn.close()

@login_manager.user_loader
def load_user(user_id):
	conn = engine.connect()
	s = conn.execute(select([users]).where(users.c.id == user_id)).fetchone()
	conn.close()
	return User(s.id, s.nome, s.email, s.image_file, s.password, s.admin)

class User(UserMixin):
    def __init__(self, id, nome, email, image_file, password, admin):
        self.id = id
        self.nome = username
        self.email = email
        self.image_file = image_file
        self.password = password
        self.admin = admin

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