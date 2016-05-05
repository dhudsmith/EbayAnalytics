from flask import Flask, render_template, url_for, redirect

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

@app.route('/exploration', methods = ['GET'])
def prod_hist():

    return render_template('data_exploration.html')

@app.route('/livefeed', methods = ['GET'])
def rf():
    return render_template('runningscore.html')

# @app.route('/livefeed', methods = ['GET'])
# def rf():
#     return redirect(url_for('static', filename='runningscore.html'))

# @app.route('/<path:path>')
# def static_proxy(path):
#   # send_static_file will guess the correct MIME type
#   return app.send_static_file(path)

# Main function
if __name__ == '__main__':
    # app.run(port=33507, debug=True)
    app.run(debug=True)

