from __future__ import print_function
from flask import Flask
from flask import render_template, flash, redirect
from flask_bootstrap import Bootstrap
import flask_login
from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData, Table, Column, Integer
import sqlalchemy as sa

db = SQLAlchemy()


app = Flask(__name__)
app.config.from_object('config')

engine = create_engine('mysql+mysqldb://ad1444:bristolad1444@db4free.net/bristolad1444')
connection = engine.connect()


# result = connection.execute("SELECT username FROM users")

# for row in result:
#     print ("username:", row['username'])
# connection.close()

  
@app.route('/testdb')
def testdb():
	if db.session.query("1").from_statement("SELECT 1").all():
		return "It works."
	else:
		return 'Something is broken.'


Bootstrap(app)
app.config['DEBUG'] = True



@app.route('/')
def index():
    """Return a friendly HTTP greeting."""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    meta = MetaData()
    users_table = Table('users', meta,
        Column('id', sa.Integer, primary_key=True),
        Column('username', sa.String(50)),
        Column('password', sa.String(100))
    )
    result = connection.execute(users_table.select(users_table.c.username == form.username.data))
    for row in result:
        passdb = row['password']
    if form.validate_on_submit() and form.password.data==passdb:
        flash('Login requested for OpenID="%s", remember_me=%s' %
              (form.username.data, str(form.remember_me.data)))
        return redirect('/home')
    return render_template('login.html', 
                           title='Sign In',
                           form=form)

@app.route('/home')
def home():
    """Home page"""
    user = {'nickname': 'Miguel'} 
    posts = [  # fake array of posts
        { 
            'author': {'nickname': 'John'}, 
            'body': 'Beautiful day in Portland!' 
        },
        { 
            'author': {'nickname': 'Susan'}, 
            'body': 'The Avengers movie was so cool!' 
        }
    ]
    return render_template('home.html',
    						title='Home',
                           	user=user,
                           	posts=posts)


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404

class LoginForm(Form):
	username = StringField('user', validators=[DataRequired()])
	password = StringField('pass', validators=[DataRequired()])
	remember_me = BooleanField('remember_me', default=False)


