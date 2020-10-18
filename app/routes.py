from app import app
from flask import request
from flask import render_template
from flask import send_file
import logging
from logging.handlers import RotatingFileHandler
import wget
import os
import math
import hashlib
import pickle
import io
import shutil


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/favicon.ico')
def favicon():
    return None

#setting up the server log
format = logging.Formatter('%(asctime)s %(message)s')
logFile = 'log.log'
my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024,
                                 backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(format)
my_handler.setLevel(logging.ERROR)

app_log = logging.getLogger('root')
app_log.setLevel(logging.DEBUG)

app_log.addHandler(my_handler)
