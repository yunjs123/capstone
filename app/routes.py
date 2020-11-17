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
import json

email = "jstrahl1@uncc.edu"
key = "bluecat44"
daily_url = "https://aqs.epa.gov/data/api/dailyData/byState?email=jstrahl1@uncc.edu&key=bluecat44&param=44201&bdate=20201110&edate=20201110&state=37"



#Default Route
@app.route('/')
def index():
    app_log.info(f"User: {request.remote_addr}")
    return render_template("home.html", data='')

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/chart')
def chart():
    return render_template("chart.html", data='')

@app.route('/favicon.ico')
def favicon():
    return ''

@app.route('/map', methods=['GET', 'POST'])
def map():
    if request.method == 'POST':
        print("POST REQUEST")
        state = request.form.get('search')
        data = download(convert_state(state))
        return render_template("chart.html", data=data)
    return "ERROR"


def convert_state(state):
    state_names = ["" , "alaska", "alabama", "arkansas", "arizona", "california", "colorado", "connecticut", "delaware", "florida", "georgia", "hawaii", "iowa", "idaho", "illinois", "indiana", "kansas", "kentucky", "louisiana", "massachusetts", "maryland", "maine", "michigan", "minnesota", "missouri", "mississippi", "montana", "north narolina", "north dakota", "nebraska", "new hampshire", "new jersey", "new mexico", "nevada", "new york", "ohio", "oklahoma", "oregon", "pennsylvania", "rhode island", "south carolina", "south dakota", "tennessee", "texas", "utah", "virginia", "vermont", "washington", "wisconsin", "west virginia", "wyoming"]
    state = state.lower() 
    num = state_names.index(state)
    print(num)
    return num


def download(location):
    url = f"https://aqs.epa.gov/data/api/dailyData/byState?email={email}&key={key}&param=44201&bdate=20200901&edate=20200901&state={location}"
    data_name = wget.download(url, out=f"app/files/{location}.json")
    with open(data_name) as f:
        data = json.load(f)
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
