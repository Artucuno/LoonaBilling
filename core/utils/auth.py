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
import random
import string
from functools import update_wrapper

hauth = HTTPBasicAuth()

def gen2FA(data):
    a = ''
    for f in range(random.randint(30,50)):
        a += random.choice(string.ascii_letters)
    if a in os.listdir('data/2fa'):
        return gen2FA()
    with open(f'data/2fa/{a}', 'w+') as of:
        json.dump(data, of)
    return a

def getUser(id):
    try:
        with open(f'data/user/{id}/config.json') as of:
            data = json.load(of)
            return data
    except:
        return False

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for('Accounts.login'))
        else:
            if isAuth(session['user']):
                if not isSuspended(json.loads(session['user'])['Config'][0]['email']):
                    return function()
                else:
                    return redirect(url_for('Accounts.suspended'))
            else:
                return redirect(url_for('Accounts.login'))

    return update_wrapper(wrapper, function)

def isEmail(email):
    for f in os.listdir('data/user'):
        try:
            with open(f'data/user/{f}/config.json') as of:
                data = json.load(of)
                for p in data['Config']:
                    #print(p['email'])
                    if p['email'] == email:
                        return True
        except Exception as e:
            print(e)
    return False

def getID(email):
    for f in os.listdir('data/user'):
        try:
            with open(f'data/user/{f}/config.json') as of:
                data = json.load(of)
                for p in data['Config']:
                    if p['email'] == email:
                        return p['ID']
        except Exception as e:
            print(e)
    return False

def isSuspended(email):
    for f in os.listdir('data/user'):
        try:
            with open(f'data/user/{f}/config.json') as of:
                data = json.load(of)
                for p in data['Config']:
                    if p['email'] == email:
                        if p['suspended']['isSuspended'] == True:
                            return p['suspended']['reason']
                        return False
        except Exception as e:
            print(e)
    return False

def logAuth(form):
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

def genState():
    a = ''
    for f in range(random.randint(10,30)):
        a += random.choice(string.ascii_letters)
    if a in os.listdir('data/states'):
        return genState()
    return a

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
