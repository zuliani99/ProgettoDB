from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect #import necessari per il funzionamento dell'applicazione
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm


app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'    #chiave necessaria per l'applicazione
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True) # va ad indicare che c'è una relazione con Post con riferimento ad author e che il caricamento deve essere effettuato in maniera immediata
    # non è una colonna effettiva della tabella

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # questa è una colonna effettiva e va ad indicare la presenza di una chiave esterna che punta a user.id

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


posts = [       #i post che visualizzaremo all'interno
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts) #mi renderizza il template home.html con variabuile post=posts, cioè passo al home.html i due post che ho inizializzato prima


@app.route("/about") #mi renderizza il template about.html con variabuile title='About'
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST']) #metodo reguister, in cui dal file form.py inizializza un nuovo RegistrationForm(),
def register():
    form = RegistrationForm()
    if form.validate_on_submit(): #controlla che tutte le regole del form siano state passate con successo
        flash(f'Account created for {form.username.data}!', 'success') # messaggio di avvenuto sing up al blog
        return redirect(url_for('home'))    # redirect alla funzione home
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])   # metodo per la fase di login, in cui da form.py inizializza un nuovo loginform
def login():
    form = LoginForm()
    if form.validate_on_submit(): #controlla che tutte le regole del form siano state passate con successo
        if form.email.data == 'admin@blog.com' and form.password.data == 'password': #test di login senza database
            flash('You have been logged in!', 'success') # messaggio con categoria (success) che poi andarà a finire nella classe della div che contiene il messaggio stesso
            return redirect(url_for('home')) # redirect alla funzione home
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger') # messaggio di login incorretta
    return render_template('login.html', title='Login', form=form)


if __name__ == '__main__': #condizione per far partirte l'applicazione senza flask run e sempre in dubug mode
    app.run(debug=True)
