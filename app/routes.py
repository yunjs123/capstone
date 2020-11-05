from app import app
from flask import request
from flask import render_template
from flask import send_file
import logging
from logging.handlers import RotatingFileHandler
import wget
import os
import math
import io
import shutil

email = "jstrahl1@uncc.edu"
key = "bluecat44"


#Default Route
@app.route('/')
def index():
    app_log.info(f"User: {request.remote_addr}")
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/favicon.ico')
def favicon():
    return None

@app.route('/search')
def search():
    state = request.args['search']
    data = download(state)
    return data

def download(location):
    url = f"https://aqs.epa.gov/data/api/list/countiesByState?email={email}&key={key}&state=37"
    data = wget.download(url)
    return data

#setting up the server log
format = logging.Formatter('%(asctime)s %(message)s')
logFile = 'log.log'
my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024,
                                 backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(format)
my_handler.setLevel(logging.INFO)

app_log = logging.getLogger('root')
app_log.setLevel(logging.DEBUG)

app_log.addHandler(my_handler)
