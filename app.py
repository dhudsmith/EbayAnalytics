from flask import Flask, render_template
import requests


app = Flask(__name__)

# App variables
app.vars = {}

# Routing
@app.route('/')
def main():
    return render_template('main.html')

@app.route('/plot1', methods = ['GET'])
def plot1():

    return render_template('plot1.html')

@app.route('/plot2', methods = ['GET'])
def plot2():

    return render_template('plot2.html')

@app.route('/plot3', methods = ['GET'])
def plot3():

    return render_template('plot3.html')

# @app.route('/rf', methods = ['GET'])
# def rf():
#     return render_template('rf.html')

@app.route('/livefeed', methods = ['GET'])
def rf():
    return render_template('livefeed.html')

# Main function
if __name__ == '__main__':
    app.run(port=33507, debug=True)

