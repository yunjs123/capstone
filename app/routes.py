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
    return ''

@app.route('/map', methods=['GET', 'POST'])
def map():
    if request.method == 'POST':
        print("POST REQUEST")
        state = request.form.get('search')
        data = download(state)
        
        return render_template("index.html", data=data)
    


    return "ERROR"


def convert_state(state):
    states = []
    num = states.index(state)
    return state


def download(location):
    url = f"https://aqs.epa.gov/data/api/dailyData/byState?email={email}&key={key}&param=45201&bdate=20200915&edate=20201101&state=37"
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
