import base64
from uuid import getnode
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask_httpauth import HTTPBasicAuth
from flask import *
import json
import sys, os

hauth = HTTPBasicAuth()

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for('Accounts.login'))
        else:
            if isAuth(session['user']):
                return function()
            else:
                return redirect(url_for('Accounts.login'))

    return wrapper

def isEmail(email):
    for f in os.listdir('data/user'):
        try:
            with open(f'data/user/{f}/config.json') as of:
                data = json.load(of)
                for p in data['Config']:
                    if p['email'] == email:
                        return True
        except:
            pass
    return False

def getID(email):
    for f in os.listdir('data/user'):
        try:
            with open(f'data/user/{f}/config.json') as of:
                data = json.load(of)
                for p in data['Config']:
                    if p['email'] == email:
                        return p['ID']
        except:
            continue
    return False

def logAuth(form):
    #print(form)
    #print(form['Config'][0]['ID'])
    try:
        with open(f'data/user/{form["Config"][0]["ID"]}/config.json') as of:
            data = json.load(of)
            for p in data['Config']:
                if p['email'] == form['Config'][0]['email']:
                    if p['password'] == form['Config'][0]['password']:
                        return data
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(e, exc_type, fname, exc_tb.tb_lineno)
    return False

def isAuth(sess):
    #print(type(sess))
    try:
        data = json.loads(sess)
        #print(data)
        for p in data['Config']:
            with open(f"data/user/{p['ID']}/config.json") as of:
                dt = json.load(of)
                for pp in dt['Config']:
                    #print(data, dt)
                    if p['email'] == pp['email']:
                        #print('email')
                        if p['password'] == pp['password']:
                            #print('password')
                            #print(dt)
                            return dt
                        else:
                            return False
    except Exception as e:
        print(e)
        return False

def getUserCount():
    return len(os.listdir('data/user'))

def encKey(adPass):
    password = adPass.encode()
    salt = str(getnode()).encode()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key

@hauth.verify_password
def verify_password(username, password):
    users = {
        "admin": open('setup', 'rb').read(),
    }
    if username in users and users["admin"] == encKey(password):
        return username
