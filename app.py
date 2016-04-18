from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# App variables
app.vars = {}

@app.route('/')
def main():
    return render_template('main.html')

# @app.route('/', methods = ['POST'])
# def form_POST():
#     # get the user input
#     app.vars['ticker'] = request.form['ticker']
#     app.vars['selected'] = request.form.getlist('features')
#
#     return redirect('/plot1')

@app.route('/plot1', methods = ['GET'])
def plot1():

    return render_template('plot1.html')

@app.route('/plot2', methods = ['GET'])
def plot2():

    return render_template('plot2.html')


if __name__ == '__main__':
    app.run(port=33507, debug=True)
