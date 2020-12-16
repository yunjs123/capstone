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
from datetime import timedelta

email = "jstrahl1@uncc.edu"
key = "bluecat44"
daily_url = "https://s3-us-west-1.amazonaws.com//files.airnowtech.org/airnow/today/HourlyData_"
yest_url = "https://s3-us-west-1.amazonaws.com//files.airnowtech.org/airnow/yesterday/HourlyData_"

risks = ["No health risks today", "If you have sensative lungs you might not want to stay outside very long today, maybe an hour at most", "No outdoor activities, children should not be out", 
"Only go outside if you really have to or atleast limit your time", "Do not go outside if you can"]

daily_data = []
yest_data = []

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
        yest_collected = []
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
            if (search in n[3].lower() or search in n[8].lower()) and (n[5] not in data_collected):
                data_collected.append(n[5])
                data_collected.append(n[6])
                data_collected.append(n[7])
                data_collected.append(compare_values(n[7]))
                if data_collected[0] != n[8]:
                    data_collected.insert(0, n[8])

        for i, n in enumerate(yest_data):
            if (search in n[3].lower() or search in n[8].lower()) and (n[5] not in yest_collected):
                yest_collected.append(n[5])
                yest_collected.append(n[6])
                yest_collected.append(n[7])
                yest_collected.append(compare_values(n[7]))
                if yest_collected[0] != n[8]:
                    yest_collected.insert(0, n[8])

        prediction = []
        temp = {}
        temp2 = {}
        print(yest_collected)
        for n, i in enumerate(yest_collected):
            if i == "OZONE":
                temp['OZONE'] = yest_collected[n+2]
            elif i =="PM2.5":
                temp['PM2.5'] = yest_collected[n+2]
            elif i == "PM10":
                temp['PM10'] = yest_collected[n+2]

        for n, i in enumerate(data_collected):
            if i == "OZONE":
                temp2['OZONE'] = data_collected[n+2]
            elif i =="PM2.5":
                temp2['PM2.5'] = data_collected[n+2]
            elif i == "PM10":
                temp2['PM10'] = data_collected[n+2]


        if ("OZONE" in temp):
            prediction.append("OZONE")
            prediction.append("PPB")
            prediction.append((float(temp.get("OZONE")) + float(temp2.get("OZONE")))/2)
            prediction.append(compare_values((float(temp.get("OZONE")) + float(temp2.get("OZONE")))/2))
        if ("PM2.5" in temp):
            prediction.append("PM2.5")
            prediction.append("UG/M3")
            prediction.append((float(temp.get("PM2.5"))+float(temp2.get("PM2.5")))/2)
            prediction.append(compare_values(float(temp.get("PM2.5"))+float(temp2.get("PM2.5")))/2)
        if ("PM10" in temp):
            prediction.append("PM10")
            prediction.append("UG/M3")
            prediction.append((float(temp.get("PM10"))+float(temp2.get("PM10")))/2)
            prediction.append(compare_values(float(temp.get("PM10"))+float(temp2.get("PM10")))/2)

        print(data_collected)
        
        data_collected.append(daily_data[4448][0])
        #4454
        return render_template("chart.html", data=data_collected, risk_list=risks, prediction=prediction)
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

    if os.path.exists(f"app/files/2020{datetime.now().strftime('%m')}{datetime.now().strftime('%d')}00.dat") and len(daily_data) > 0:
        with open(f"app/files/2020{datetime.now().strftime('%m')}{datetime.now().strftime('%d')}00.dat", encoding='utf-8') as file1:
            Lines = file1.readlines()
            for line in Lines:
                daily_data.append(line.split("|"))
        load_loca()
        return
    else:
        print("Downlaoding from API")
        print(daily_url + f"2020{datetime.now().strftime('%m')}{datetime.now().strftime('%d')}.dat")
        data_name = wget.download(daily_url + f"2020{datetime.now().strftime('%m')}{datetime.now().strftime('%d')}00.dat", out=f"app/files/2020{datetime.now().strftime('%m')}{datetime.now().strftime('%d')}00.dat")
        print("Downlaoded from API")
        with open(f"app/files/2020{datetime.now().strftime('%m')}{datetime.now().strftime('%d')}00.dat", encoding='utf-8') as file1:
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

def next_day():
    pred = ""

    return pred

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


if os.path.exists(f"app/files/2020{datetime.now().strftime('%m')}{datetime.now().strftime('%d')}00.dat"):
        with open(f"app/files/2020{datetime.now().strftime('%m')}{datetime.now().strftime('%d')}00.dat", encoding='utf-8') as file1:
            Lines = file1.readlines()
            for line in Lines:
                daily_data.append(line.split("|"))
        load_loca()
prev_day = datetime.today() - timedelta(days=1)
prev_day_form = prev_day.strftime ('%Y%m%d')

# https://s3-us-west-1.amazonaws.com//files.airnowtech.org/airnow/yesterday/HourlyData_2020121500.dat
if not os.path.exists(f"app/files/{str(prev_day_form)}00.dat"):
    print(yest_url + f"{str(prev_day_form)}00.dat")
    wget.download(yest_url + f"{str(prev_day_form)}00.dat", out=f"app/files/{str(prev_day_form)}00.dat")
    with open(f"app/files/{str(prev_day_form)}00.dat" , encoding='utf-8') as file2:
            Lines = file2.readlines()
            for line in Lines:
                yest_data.append(line.split("|"))
else:
    with open(f"app/files/{str(prev_day_form)}00.dat" , encoding='utf-8') as file2:
            Lines = file2.readlines()
            for line in Lines:
                yest_data.append(line.split("|"))