import time
import logging
logging.basicConfig(filename='logs/'+str(time.time()),
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
import sys, os
import json
from flask import Flask
from flask import *
import stripe
import config
import string
import random
import imp
from colorama import Fore, Back, Style
from colorama import init
import psutil
import base64
from uuid import getnode
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from art import *
import requests

tprint("LoonaBilling")
init()

app = Flask(__name__)
app.adminModules = []
app.version = '1.2'
app.hasUpdate = False

def cf(folder):
    try:
        os.mkdir(folder)
        print(f'[LoonaBilling] Created Folder: {folder}')
    except Exception as e:
        return

def checks():
    cf('configs')
    cf('modules')
    cf('modules/user')
    cf('modules/admin')
    cf('core')
    cf('core/payments')
    cf('products')
    cf('logs')
    try:
        x = requests.get('https://raw.githubusercontent.com/Loona-cc/LoonaBilling/main/version').text
        if x.text.strip() != app.version:
            app.hasUpdate = True
    except:
        print('Unable to get latest version')

checks()

def load_blueprints():
    mods = {}
    #path = 'modules'
    #dir_list = os.listdir(path)

    for path, dirs, files in os.walk("modules", topdown=False):
        for fname in files:
            try:
                name, ext = os.path.splitext(fname)
                if ext == '.py' and not name == '__init__':
                    f, filename, descr = imp.find_module(name, [path])
                    mods[fname] = imp.load_module(name, f, filename, descr)
                    #print(getattr(mods[fname]))
                    app.register_blueprint(getattr(mods[fname], 'module'), url_prefix=f'/{name}')
                    print(Fore.GREEN + '[Module] ' + Style.RESET_ALL + 'Imported', mods[fname].module.name)
                    #globals()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(Fore.RED, '[ERROR]', path, name, e, exc_type, fname, exc_tb.tb_lineno, Style.RESET_ALL)

    for path, dirs, files in os.walk("core", topdown=False):
        for fname in files:
            try:
                name, ext = os.path.splitext(fname)
                if ext == '.py' and not name == '__init__':
                    f, filename, descr = imp.find_module(name, [path])
                    mods[fname] = imp.load_module(name, f, filename, descr)
                    app.register_blueprint(getattr(mods[fname], 'module'))#, url_prefix=f'/{name}')
                    print(Fore.GREEN + '[Core] ' + Style.RESET_ALL + 'Imported', mods[fname].module.name)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(Fore.RED, '[ERROR]', path, name, e, exc_type, fname, exc_tb.tb_lineno, Style.RESET_ALL)
    return mods

mods = load_blueprints()
#print(app.url_map)
#print(mods)
for f in mods:
    #print(f)
    try:
        if mods[f].module.hasAdminPage == True:
            app.adminModules += [mods[f].module.name]
        #print(f, mods[f].module.name, mods[f].module.hasAdminPage, mods[f].module.version)
    except:
        pass

@app.route('/admin')
def admin():
    return render_template('core/admin.html', tabs=app.adminModules, map=app.url_map, cpuUsage=int(psutil.cpu_percent()), ramUsage=int(psutil.virtual_memory().percent), storageUsage=int(psutil.disk_usage('/').percent))

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html', businessName=config.businessName), 404

if __name__ == '__main__':
    app.config['SERVER_NAME'] = config.domain
    if app.hasUpdate:
        print(Fore.GREEN + '[LoonaBilling] ' + Style.RESET_ALL + '*** There is a new update! ***')
    print(Fore.GREEN + '[LoonaBilling] ' + Style.RESET_ALL + 'Ready to start')
    app.run(host=config.ip, port=config.port, debug=config.debug, ssl_context=config.ssl)
