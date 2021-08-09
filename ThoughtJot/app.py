from flask import Flask, render_template, flash, redirect, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from datetime import datetime
from functools import wraps
from flask_cors import CORS
import string
import secrets
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.recaptcha import validators
from wtforms import StringField
from wtforms.fields.core import BooleanField
from wtforms.fields.simple import PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError


# Configure application
app = Flask(__name__)
CORS(app)

app.config["SECRET_KEY"] = "88a15f8443b89169600f9fd940b624f4"

# Configures database location 
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///thoughtjot.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initializes database 
db = SQLAlchemy(app)

# Creates database model for User table which stores all users who register
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(18), unique=True, nullable=False)
    password = db.Column(db.String(102), nullable=False)
    key = db.Column(db.String(6), unique=True)
    jots = db.relationship("Jot", backref="author", lazy=True)
    
    def __repr__(self): 
        return f"User('{self.id}', '{self.username}')"
    
# Creates database model for Jot table which stores all notes made by users
class Jot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(10000))
    url = db.Column(db.String(500))
    submit_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    category = db.Column(db.String(200)) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Jot('{self.id}', '{self.url}', '{self.user_id}', '{self.category}','{self.submit_date}','{self.message}')"



# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Taken from helpers.py in CS50 Finance
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            # ADD FLASH POSSIBILITY TO EXPLAIN REDIRECT 
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# Creates a unique 6 character alphanumeric string to use for user identification
# between the chrome extension and web app.
# Creates a new key in case of a match 
def generate_key():
    matching = True
    alphabet = string.ascii_uppercase + string.digits
    while matching:
        password = ''.join(secrets.choice(alphabet) for i in range(6))
        users = User.query.all()
        matching = False
        for user in users:
            if user.key == password:
                matching = True
    return password
    

# Builds registration form using WTForms
class registrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=18)])
    password = PasswordField('Password', validators=[DataRequired()])
    password_confirmation = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', 'Passwords do not match.')])
    submit = SubmitField('Register')

# Builds login form to using WTForms
class loginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=18)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')


# Default route which serves as a dashboard for viewing all noted content when
# logged in to the app.
@app.route("/")
@login_required
def index():
    rows = Jot.query.filter_by(user_id=session["user_id"]).all()
    return render_template("logs.html", rows=rows)


# Registration route used to collect and validate user input while also inputting it
# into the database 
@app.route("/register", methods=["GET","POST"])
def register():
    form = registrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=generate_password_hash(form.password.data), key=generate_key())
        existing_username = User.query.filter_by(username = form.username.data).first()
        if existing_username:
            flash(f"'{form.username.data}' is already taken.", category="danger")
            return redirect("/register")

        db.session.add(user)
        db.session.commit()
        
        session["user_id"] = user.id

        flash(f"{form.username.data} has been registered! Press the 'Get Key' option in the navigation bar to get started!", category="success")
        return redirect("/")

    return render_template("register.html", form=form)

# Login route which collects and validates a users login information and creates
# their session 
@app.route("/login", methods=["GET", "POST"])
def login():
    form = loginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                session["user_id"] = user.id
                
                flash(f"Welcome, {form.username.data}!", category="success")
                # Will be changed to log view page but this is a temp test redirect
                return redirect("/")
            else:
                flash("Invalid username/password.", category="danger")
        else:
            flash("This user does not exist!", category="danger")
            redirect("/login")
    return render_template("login.html", form=form)

# Log route which is accessed by the chrome extension for sending JSON data
# which is then converted and displayed in a table on the default route
@app.route("/log", methods=["POST"])
def log():
    logged = request.get_json(force=True)

    user = User.query.filter_by(key=logged["key"]).first()

    if user:
        jot = Jot(message=logged["text"], url=logged["location"], user_id=user.id)
        db.session.add(jot)
        db.session.commit()
        return "Log was successful"
    return "Log was unsuccessful"

# Key route which is used to display a users ThoughtJot key so that they can
# paste it into their chrome extension. It also allows users to generate a new 
# key in the event that their current one was compromised.
@app.route("/key", methods=["GET", "POST"])
@login_required
def key():
    if request.method == "POST":
        user = User.query.filter_by(id = session["user_id"]).first()
        user.key = generate_key()
        db.session.commit()
        flash("Key updated successfully. Make sure to update it in the extension options!", category="success")
        return redirect("/key")
    else:
        user = User.query.filter_by(id = session["user_id"]).first()
        return render_template("key.html", key=user.key)

# The help route is a guide to configuring the chrome extension to send data
# to the correct user's account
@app.route("/help")
@login_required
def help():
    return render_template("help.html")

# Logout route used for clearing session data
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
