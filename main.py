from __future__ import print_function
from flask import Flask
from flask import render_template, flash, redirect
from flask_bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired
from google.appengine.api import users

import os


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


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404
