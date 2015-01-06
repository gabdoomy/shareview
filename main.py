from __future__ import print_function
from flask import Flask, render_template, flash, redirect, request, make_response
from flask_bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired
from werkzeug.http import parse_options_header, parse_cache_control_header, parse_set_header, dump_header

import os
import urllib
import urllib2
import webapp2
import requests
import json

from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

import MySQLdb
import time
from collections import defaultdict

app = Flask(__name__)
app.config.from_object('config')

Bootstrap(app)
app.config['DEBUG'] = True

env = os.getenv('SERVER_SOFTWARE')
if (env and env.startswith('Google App Engine/')):
# Connecting from App Engine
    db = MySQLdb.connect(
    unix_socket='/cloudsql/bristoluni-cloud-ad1444:us-instance-copy1',
    user='root')
    db.close()
    db = MySQLdb.connect(
    unix_socket='/cloudsql/bristoluni-cloud-ad1444:us-instance-copy1',
    user='root')
else:
# You may also assign an IP Address from the access control
# page and use it to connect from an external network.
    db = MySQLdb.connect(host='173.194.110.240', port=3306, db='shareview', user='root', passwd='password')
    db.close()
    db = MySQLdb.connect(host='173.194.110.240', port=3306, db='shareview', user='root', passwd='password')

#cursor.execute('CREATE DATABASE shareview;')
#cursor.execute('CREATE TABLE IF NOT EXISTS shareview.users (ID INT NOT NULL AUTO_INCREMENT,  username VARCHAR(255),  password VARCHAR(255),  PRIMARY KEY(ID));')
#cursor.execute('SELECT ID, username, password from shareview.users;')

#userlist = [];
#for row in cursor.fetchall():
#    userlist.append(dict([('ID',row[0]),
#                         ('username',row[1]),
#                         ('password',row[2])
#                        ]))

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
    cursor=db.cursor()
    cursor.execute("SELECT * FROM shareview.photos WHERE user=\""+str(user)+"\" ORDER BY city ASC, date DESC, time DESC;")
    # photos = [];
    # cities_list=[];
    # for row in cursor.fetchall():
    #     cities_list.append(row[5]);
    #     cities=set(cities_list);
    dictionary = defaultdict(list)
    for row in cursor.fetchall():
        dictionary[str(row[5])]=[row[3],row[4]]
    cursor.execute("SELECT * FROM shareview.photos WHERE user=\""+str(user)+"\" ORDER BY city ASC, date DESC, time DESC;")
    for row in cursor.fetchall():
        dictionary[str(row[5])].append(row[1])
    # for key, value in dictionary.items() :
    #     print (key, value)
    logout_url=""
    if user:
            logout_url = users.create_logout_url('/')
    json_string = str(json.dumps(dictionary))
    return render_template('home.html',
                            title='Home',
                            data=json_string,
                            user=user.nickname(),
                            logout=logout_url)

def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

@app.route('/profile')
def profile():
    """Profile page"""
    user = users.get_current_user()
    cursor=db.cursor()
    dictionary = defaultdict(list)
    cursor.execute("SELECT * FROM shareview.photos WHERE user=\""+str(user)+"\" ORDER BY city ASC, date DESC, time DESC;")
    for row in cursor.fetchall():
        dictionary[str(row[5])].append(row[1])
    for key, value in dictionary.items() :
        print (key, value)
    size=cursor.fetchone()
    cityname="null"
    print(str(size))
    if(str(size)=="None"):
        json_string=""
    else:
        for row in cursor.fetchall():
            cityname=str(row[5])
    json_string = str(json.dumps(dictionary))
    logout_url=""
    if user:
            logout_url = users.create_logout_url('/')
    return render_template('profile.html',
                            title='Profile',
                            data=json_string,
                            city=cityname,
                            user=user.nickname(),
                            logout=logout_url)

@app.route('/collage')
def collage():
    """Photo Collage page"""
    user = users.get_current_user()
    cursor=db.cursor()
    dictionary = defaultdict(list)
    cursor.execute("SELECT * FROM shareview.photos WHERE user=\""+str(user)+"\" ORDER BY city ASC, date DESC, time DESC;")
    for row in cursor.fetchall():
        dictionary[str(row[5])].append(row[1])
    for key, value in dictionary.items() :
        print (key, value)
    size=cursor.fetchone()
    cityname="null"
    print(str(size))
    if(str(size)=="None"):
        json_string=""
    else:
        for row in cursor.fetchall():
            cityname=str(row[5])
    json_string = str(json.dumps(dictionary))
    logout_url=""
    if user:
            logout_url = users.create_logout_url('/')
    return render_template('collage.html',
                            title='Profile',
                            data=json_string,
                            city=cityname,
                            user=user.nickname(),
                            logout=logout_url)

@app.route('/mainupload')
def mainupload():
    user = users.get_current_user()
    upload_url = blobstore.create_upload_url('/upload')
    logout_url=""
    if user:
            logout_url = users.create_logout_url('/')
    return render_template('mainupload.html',
                    title='Upload',
                    upload_url=upload_url,
                    user=user.nickname(),
                    logout=logout_url)

@app.route('/upload', methods=['POST'])
def post():
    #city = request.params['city']
    #print(city)
    if request.method == 'POST':
        user = users.get_current_user()
        file = request.files['file']
        city =  request.form["city"]
        request_string = urllib2.Request ('http://nominatim.openstreetmap.org/search?q='+city+'&format=json')
        response = urllib2.urlopen (request_string)
        json_string = json.loads(response.read())
        lat = json_string[0]["lat"]
        lon = json_string[0]["lon"]
        city_name = json_string[0]["display_name"]
        print(city_name.encode("utf-8"))
        header = file.headers['Content-Type']
        parsed_header = parse_options_header(header)
        blob_key = parsed_header[1]['blob-key']
        statement='INSERT INTO shareview.photos (name, user, lat, lon, city, date, time) values (\"'+str(blob_key)+'\",\"'+str(user)+'\",'+str(lat)+','+str(lon)+',\"'+str(city_name.encode("utf-8"))+'\",\"'+str(time.strftime("%Y-%m-%d"))+'\",\"'+str(time.strftime("%H:%M:%S"))+ '\");'
        statement=statement.encode("utf-8")
        db.cursor().execute(statement)
        db.commit()
        logout_url=""
        if user:
                logout_url = users.create_logout_url('/')
        return render_template('uploadresult.html',
                    title='Upload Done',
                    user=user.nickname(),
                    statement=statement,
                    logout=logout_url)
        #'INSERT INTO shareview.photos (name, user, lat, lon, city, date, time) values (\"'+str(blob_key)+'\",\"'+str(user)+'\",'+str(lat)+','+str(lon)+',\"'+str(city_name)+'\",\"'+str(time.strftime("%Y-%m-%d")) +'\",\"'+str(time.strftime("%H:%M:%S")) +'\");'
        #blob_key+"<br>lat: "+lat+"<br>lon: "+lon+"<br>City: "+city_name+"<br>date:"+time.strftime("%Y-%m-%d")+"<br>time:"+time.strftime("%H:%M:%S")

@app.route("/gallery/<lat>/<lon>")
def creategallery(lat, lon):
    user = users.get_current_user()
    cursor=db.cursor()
    dictionary = defaultdict(list)
    cursor.execute("SELECT * FROM shareview.photos WHERE user=\""+str(user)+"\" AND lat=\""+lat+"\" AND lon=\""+lon+"\" ORDER BY city ASC, date DESC, time DESC;")
    for row in cursor.fetchall():
        dictionary[str(row[5])].append(row[1])
    for key, value in dictionary.items() :
        print (key, value)
    json_string = str(json.dumps(dictionary))
    if user:
            logout_url = users.create_logout_url('/')
    return render_template('gallery.html',
                            title='Gallery',
                            data=json_string,
                            city=str(row[5]),
                            user=user.nickname(),
                            logout=logout_url)

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

