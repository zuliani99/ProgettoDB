from flaskblog import login_manager, app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy import *
from datetime import datetime

engine = create_engine('sqlite:////tmp/test.db', echo=True)
metadata = MetaData()
users = Table('users', metadata,
	Column('id', Integer, primary_key=True),
	Column('username', String(20), unique=True, nullable=False),
	Column('email', String(120), unique=True, nullable=False),
	Column('image_file', String(20), nullable=False, default='default.jpg'),
	Column('password', String(60), nullable=False)
)

posts = Table('posts', metadata,
	Column('id', Integer, primary_key=True),
	Column('title', String(100), nullable=False),
	Column('date_posted', DateTime, nullable=False, default=datetime.utcnow),
	Column('content', Text, nullable=False),
	Column('user_id', Integer, ForeignKey('users.id'), nullable=False)
)

metadata.create_all(engine)



@login_manager.user_loader
def load_user(user_id):
	conn = engine.connect()
	s = conn.execute(select([users]).where(users.c.id == user_id)).fetchone()
	conn.close()
	return User(s.id, s.username, s.email, s.image_file, s.password)


class Post():
	def __init__(self, id, title, date_posted, content, user_id):
		self.id = id
		self.title = title
		self.date_posted = date_posted
		self.content = content
		self.user_id = user_id

class User(UserMixin):
    def __init__(self, id, username, email, image_file, password):
        self.id = id
        self.username = username
        self.email = email
        self.image_file = image_file
        self.password = password

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
        return "User('{self.username}', '{self.email}', '{self.image_file}')"

