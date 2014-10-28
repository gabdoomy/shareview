from __future__ import print_function
from flask import Flask
from flask import render_template, flash, redirect, request, make_response
from flask_bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired
from werkzeug.http import parse_options_header, parse_cache_control_header, parse_set_header, dump_header

import os
import urllib
import urllib2
import webapp2

from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

import requests
import json

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

@app.route('/profile')
def profile():
    """Profile page"""
    user = users.get_current_user()
    return render_template('profile.html',
                            title='Profile',
                            user=user.nickname())

@app.route('/mainupload')
def mainupload():
    user = users.get_current_user()
    upload_url = blobstore.create_upload_url('/upload')
    return render_template('mainupload.html',
                    title='Upload',
                    upload_url=upload_url,
                    user=user.nickname())

@app.route('/upload', methods=['POST'])
def post():
    #city = request.params['city']
    #print(city)
    if request.method == 'POST':
        file = request.files['file']
        city =  request.form["city"]
        request_string = urllib2.Request ('http://nominatim.openstreetmap.org/search?q='+city+'&format=json')
        response = urllib2.urlopen (request_string)
        json_string = json.loads(response.read())
        lat = json_string[0]["lat"]
        lon = json_string[0]["lon"]
        city_name = json_string[0]["display_name"]
        header = file.headers['Content-Type']
        parsed_header = parse_options_header(header)
        blob_key = parsed_header[1]['blob-key']
        return blob_key+"<br>lat: "+lat+"<br>lon: "+lon+"<br>City: "+city_name

@app.route("/img/<bkey>")
def img(bkey):
    blob_info = blobstore.get(bkey)
    response = make_response(blob_info.open().read())
    response.headers['Content-Type'] = blob_info.content_type
    return response
    

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

