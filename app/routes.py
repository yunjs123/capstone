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
daily_url = "https://s3-us-west-1.amazonaws.com//files.airnowtech.org/airnow/today/HourlyData_2020111700.dat"

daily_data = []

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
        data = daily_data[4446]
        return render_template("chart.html", data=data)
    return "ERROR"


def convert_state(state):
    num = 0
    state_names = ["" , "alaska", "alabama", "arkansas", "arizona", "california", "colorado", "connecticut", "delaware", "florida", "georgia", "hawaii", "iowa", "idaho", "illinois", "indiana", "kansas", "kentucky", "louisiana", "massachusetts", "maryland", "maine", "michigan", "minnesota", "missouri", "mississippi", "montana", "north narolina", "north dakota", "nebraska", "new hampshire", "new jersey", "new mexico", "nevada", "new york", "ohio", "oklahoma", "oregon", "pennsylvania", "rhode island", "south carolina", "south dakota", "tennessee", "texas", "utah", "virginia", "vermont", "washington", "wisconsin", "west virginia", "wyoming"]
    states = ["", "al", "ak", "az", "ar", "ca", "co", "ct", "de", "fl", "ga", 
          "hi", "id", "il", "in", "ia", "ks", "ky", "la", "me", "md", 
          "ma", "mi", "mn", "ms", "mo", "mt", "ne", "nv", "nh", "nj", 
          "nm", "ny", "nc", "nd", "oh", "ok", "or", "pa", "ri", "sc", 
          "sd", "tn", "tx", "ut", "vt", "va", "wa", "wv", "wi", "wy"]
    state = state.lower()
    try:
        num = state_names.index(state)+3
    except:
        if num == 0:
            num = states.index(state.lower())+2
    
    return num


def download(location):
    #url = f"https://aqs.epa.gov/data/api/dailyData/bySite?email={email}&key={key}&param=44201&bdate=20201001&edate=20201002&state={location}&county=119&site=0046"

    if os.path.exists(f"app/files/daily.dat") and len(daily_data) > 0:
        with open('app/files/daily.dat', encoding='utf-8') as file1:
            Lines = file1.readlines()
            for line in Lines:
                daily_data.append(line.split("|"))
        return
    else:
        data_name = wget.download(daily_url, out=f"app/files/daily.dat")
        print("Downlaoded from API")
        with open('app/files/daily.dat', encoding='utf-8') as file1:
            Lines = file1.readlines()
            for line in Lines:
                daily_data.append(line.split("|"))
        return

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


if os.path.exists(f"app/files/daily.dat"):
        with open('app/files/daily.dat', encoding='utf-8') as file1:
            Lines = file1.readlines()
            for line in Lines:
                daily_data.append(line.split("|"))
        