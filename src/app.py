from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)

# Simple frontend
@app.route('/')
def index():
    return 'Web App with Python Flask!'

''' 
# EXAMPLE FRONTEND
# Follow: https://projects.raspberrypi.org/en/projects/python-web-server-with-flask
@app.route('/')
def index():
    return render_template('index.html')
'''

'''
# EXAMPLE BACKEND
# An example of completing some logic and returning data in JSON
@app.route('/time/')
def time():
    from datetime import datetime
    now = datetime.now()
    return(
        jsonify(time=now.strftime("%H:%M:%S"))
    )
'''

'''
# EXAMPLE DYNAMIC FRONTEND
# An example of how to pass parameters from the URL into the app
@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)
'''

if __name__ == "__main__":
    
    # set port to host server
    if os.environ.get('PORT'):
        port = os.environ.get('PORT')
    else:
        port = 5000

    app.run(host='0.0.0.0', port=port, debug=True)
