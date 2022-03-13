"""
Python 3.9 
didkit 0.3.0 get_version
"""
from flask import Flask, jsonify
from flask_qrcode import QRcode
import didkit
import redis
import os
import time

# local dependencies
from routes import login, onboarding
import environment

# init
myenv = os.getenv('MYENV')
if not myenv :
   myenv='local'
mode = environment.currentMode(myenv)
app = Flask(__name__)
qrcode = QRcode(app)
app.jinja_env.globals['Version'] = "0.2"
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_COOKIE_NAME'] = 'talao'
app.config['SESSION_TYPE'] = 'redis' # Redis server side session
app.config['SESSION_FILE_THRESHOLD'] = 100
app.config['SECRET_KEY'] = "talao_gaiax-sandbox"

# Redis est utilisé pour stocker les données de session
red= redis.Redis(host='localhost', port=6379, db=0)

# init routes 
login.init_app(app, red, mode)
onboarding.init_app(app, red, mode)

print("didkit version = ", didkit.get_version())

@app.route('/gaiax' , methods=['GET']) 
def test() :
   return jsonify("Bonjour")

# MAIN entry point. Flask http server
if __name__ == '__main__':
    app.run(host = mode.IP, port= mode.port, debug=True)