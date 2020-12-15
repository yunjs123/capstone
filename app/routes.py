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
from datetime import datetime

email = "jstrahl1@uncc.edu"
key = "bluecat44"
daily_url = "https://s3-us-west-1.amazonaws.com//files.airnowtech.org/airnow/today/HourlyData_"

risks = ["No health risks today", "If you have sensative lungs you might not want to stay outside very long today, maybe an hour at most", "No outdoor activities, children should not be out", 
"Only go outside if you really have to or atleast limit your time", "Do not go outside if you can"]

daily_data = []

loca = []

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

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/favicon.ico')
def favicon():
    return ''

@app.route('/map', methods=['GET', 'POST'])
def map():
    if request.method == 'POST' or request.args.get("location") is not None:
        data_collected = []
        print("POST REQUEST")
        if request.method == 'POST':
            state = request.form.get('search')
        else:
            state = request.args.get("location")
        data = download()
        load_loca()
        search = convert_string(state)
        print(search)
        for i, n in enumerate(daily_data):
            if search in n[3].lower() or search in n[8].lower():
                data_collected.append(n[5])
                data_collected.append(n[6])
                data_collected.append(n[7])
                data_collected.append(compare_values(n[7]))
                if data_collected[0] != n[8]:
                    data_collected.insert(0, n[8])
                
        print(data_collected)
        
        data_collected.append(daily_data[4448][0])
        #4454
        return render_template("chart.html", data=data_collected, risk_list=risks)
    return render_template("chart.html", data='')

@app.route('/places')
def places():
    return render_template("list.html", data=loca)


def convert_string(search):
    num = 0
    state_names = ["" , "alaska", "alabama", "arkansas", "arizona", "california", "colorado", "connecticut", "delaware", "florida", "georgia", "hawaii", "iowa", "idaho", "illinois", "indiana", "kansas", "kentucky", "louisiana", "massachusetts", "maryland", "maine", "michigan", "minnesota", "missouri", "mississippi", "montana", "north narolina", "north dakota", "nebraska", "new hampshire", "new jersey", "new mexico", "nevada", "new york", "ohio", "oklahoma", "oregon", "pennsylvania", "rhode island", "south carolina", "south dakota", "tennessee", "texas", "utah", "virginia", "vermont", "washington", "wisconsin", "west virginia", "wyoming"]
    states = ["", "al", "ak", "az", "ar", "ca", "co", "ct", "de", "fl", "ga", 
          "hi", "id", "il", "in", "ia", "ks", "ky", "la", "me", "md", 
          "ma", "mi", "mn", "ms", "mo", "mt", "ne", "nv", "nh", "nj", 
          "nm", "ny", "nc", "nd", "oh", "ok", "or", "pa", "ri", "sc", 
          "sd", "tn", "tx", "ut", "vt", "va", "wa", "wv", "wi", "wy"]
    search = search.lower()
    for i, ele in enumerate(states):
        if search in ele:
            search = state_names[i]
            break
    return search


def download():
    #url = f"https://aqs.epa.gov/data/api/dailyData/bySite?email={email}&key={key}&param=44201&bdate=20201001&edate=20201002&state={location}&county=119&site=0046"

    if os.path.exists(f"app/files/daily.dat") and len(daily_data) > 0:
        with open('app/files/daily.dat', encoding='utf-8') as file1:
            Lines = file1.readlines()
            for line in Lines:
                daily_data.append(line.split("|"))
        load_loca()
        return
    else:
        data_name = wget.download(daily_url + f"2020{datetime.now().strftime('%m')}{datetime.now().strftime('%d')}.dat", out=f"app/files/daily.dat")
        print("Downlaoded from API")
        with open('app/files/daily.dat', encoding='utf-8') as file1:
            Lines = file1.readlines()
            for line in Lines:
                daily_data.append(line.split("|"))
        load_loca()
        return

#Air quality index basic evaluation 
def compare_values(sev):
    sev = float(sev)
    if sev <= 50:
        level = 0
    elif sev > 50 and sev <= 100:
        level = 1
    elif sev > 100 and sev <= 150:
        level = 2
    elif sev > 150 and sev <= 200:
        level = 3
    elif sev > 200:
        level = 4
    return level

def load_loca():
    for x in daily_data:
        if x[8] not in loca:
            loca.append(x[8])
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
        load_loca()
        