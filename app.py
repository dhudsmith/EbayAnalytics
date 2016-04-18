from flask import Flask, render_template, request, redirect
from bokeh.plotting import figure
import requests
import json
import pandas as pd
import numpy as np

app = Flask(__name__)

# App variables
app.vars = {}

@app.route('/', methods = ['GET'])
def form_GET():
    return render_template('form.html')

@app.route('/', methods = ['POST'])
def form_POST():
    # get the user input
    app.vars['ticker'] = request.form['ticker']
    app.vars['selected'] = request.form.getlist('features')

    return redirect('/plot1')

@app.route('/plot1', methods = ['GET'])
def plot():

    return render_template('/plot1.html')


if __name__ == '__main__':
    app.run(port=33507, debug=True)
