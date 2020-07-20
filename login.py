from flask_login import *
app.config['SECRET_KEY']= 'ubersecret'
login_manager = LoginManager()
login_manager.init_app(app)
app = Flask(__name__)

class User(UserMixin)
    def __init__(self, id, email, pwd):
        seld.id=id
        self.email=email
        self.pwd=pwd

#La callback user loader ha il compito di trasformare un identificativo
#utente in un’istanza della classe User:
@login_manager.user_loader # attenzione a questo !
    def load_user(user_id):
        conn = engine.connect()
        rs = conn.execute('SELECT * FROM Users WHERE id = ? ', user_id)
        user = rs.fetchone()
        conn.close()
        return User(user.id, user.email, user.pwd)

