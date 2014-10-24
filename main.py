from __future__ import print_function
from flask import Flask
from flask import render_template, flash, redirect
from flask_bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired
from google.appengine.api import users

import os
import MySQLdb


app = Flask(__name__)
app.config.from_object('config')

env = os.getenv('SERVER_SOFTWARE')
if (env and env.startswith('Google App Engine/')):
# Connecting from App Engine
    db = MySQLdb.connect(
    unix_socket='/cloudsql/bristoluni-ad-1444:us-instance',
    user='root')
else:
  # You may also assign an IP Address from the access control
# page and use it to connect from an external network.
    db = MySQLdb.connect(host='173.194.254.24', port=3306, db='shareview', user='root', passwd='password')

cursor = db.cursor()
#cursor.execute('CREATE DATABASE shareview;')
#cursor.execute('CREATE TABLE IF NOT EXISTS shareview.users (ID INT NOT NULL AUTO_INCREMENT,  username VARCHAR(255),  password VARCHAR(255),  PRIMARY KEY(ID));')
cursor.execute('SELECT ID, username, password from shareview.users;')

userlist = [];
for row in cursor.fetchall():
    userlist.append(dict([('ID',row[0]),
                         ('username',row[1]),
                         ('password',row[2])
                         ]))


  
@app.route('/testdb')
def testdb():
	if db.session.query("1").from_statement("SELECT 1").all():
		return "It works."
	else:
		return 'Something is broken.'


Bootstrap(app)
app.config['DEBUG'] = True

@app.route('/logingoogle')
def check():
    response = check_login()
    return response

@app.route('/')
def index():
    """Return a friendly HTTP greeting."""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    result='password'
    cursor.execute('SELECT password from shareview.users where username=\"'+MySQLdb.escape_string(str(form.username.data))+'\";')
    for row in cursor.fetchall():
        result = row[0]
    if form.validate_on_submit() and form.password.data==result:
        flash("Logged in successfully.")
        flash('Login requested for OpenID="%s", remember_me=%s' %
              (form.username.data, str(form.remember_me.data)))
        return redirect('/home')
    return render_template('login.html', 
                           title='Sign In',
                           form=form)

@app.route('/home')
def home():
    """Home page"""
    user = users.get_current_user()
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
                           	user=user.nickname(),
                           	posts=posts)


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404

def check_auth():
    user = users.get_current_user()
    if user:
        greeting = ('Welcome, %s! (<a href="%s">sign out</a>)' %
                    (user.nickname(), users.create_logout_url('/')))
    else:
        greeting = ('<a href="%s">Sign in or register</a>.' %
                    users.create_login_url('/'))

    return ('<html><body>%s</body></html>' % greeting)

def check_login():
    user = users.get_current_user()
    if user:
        greeting = ('Welcome, %s! (<a href="%s">sign out</a>)' %
                    (user.nickname(), users.create_logout_url('/')))
    else:
        greeting = ('<a href="%s">Sign in or register</a>.' %
                    users.create_login_url('/'))
    return greeting

class LoginForm(Form):
	username = StringField('user', validators=[DataRequired()])
	password = StringField('pass', validators=[DataRequired()])
	remember_me = BooleanField('remember_me', default=False)



