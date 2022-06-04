import sys, os
import json
from flask import Flask
from flask import *
app = Flask(__name__)

@app.route('/')
def main():
    return 'yay it works!'

app.run(host='0.0.0.0', port=80, debug=True)
