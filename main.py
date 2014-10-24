from __future__ import print_function
from flask import Flask
from flask import render_template, flash, redirect
from flask_bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired

import os
import urllib
import webapp2

from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers


app = Flask(__name__)
app.config.from_object('config')

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

@app.route('/home')
def home():
    """Home page"""
    user = users.get_current_user()
    return render_template('home.html',
                            title='Home',
                            user=user.nickname())

@app.route('/mainupload')
def mainupload():
    upload_url = blobstore.create_upload_url('/upload')
    return('<html><body><form action="%s" method="POST" enctype="multipart/form-data">Upload File: <input type="file" name="file"><br> <input type="submit" name="submit" value="Submit"> </form></body></html>' % upload_url)

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
