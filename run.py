import time
import logging
lf = True
if lf == True:
    logging.basicConfig(filename='logs/'+str(time.time())+'.log',
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
import sys, os
import json
from flask import Flask
from flask import *
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
import getpass
import git
from werkzeug.security import generate_password_hash, check_password_hash
from core.utils.auth import hauth

print(os.getpid()) # Checking resource usage for pid
tprint("LoonaBilling")
init()

app = Flask(__name__)
app.adminModules = []
app.loadedModules = []
app.version = '1.6'
app.hasUpdate = False
app.secret_key = str(getnode()).encode()

def cf(folder):
    try:
        os.mkdir(folder)
        print(f'[LoonaBilling] Created Folder: {folder}')
    except Exception as e:
        return

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

def checks():
    cf('configs')
    cf('modules')
    cf('modules/user')
    cf('modules/admin')
    cf('core')
    cf('products')
    cf('logs')
    try:
        x = requests.get('https://raw.githubusercontent.com/Loona-cc/LoonaBilling/main/version', timeout=3)
        if x.text.strip() != app.version:
            app.hasUpdate = True
        else:
            print('You are on the latest version!')
    except Exception as e:
        print('Unable to get latest version: {}'.format(e))
    if not os.path.isfile('setup'):
        tprint("Setup")
        adPass = getpass.getpass('Enter new admin password >>> ')
        key = encKey(adPass)
        #input(key)
        with open('setup', 'wb') as of:
            of.write(key)
        of.close()
        print('=================')
        print('''Welcome to LoonaBilling! (v{})

To get started, make sure that you have configured config.py to the correct settings.
The config.py has some of the most important options such as where your LoonaBilling instance is pointed to, Debug and SSL Settings.

After you have done that, visit:
{}admin

https://github.com/Loona-cc/LoonaBilling
'''.format(app.version, config.domain_url))
        input('Press enter to continue.')

checks()

def load_blueprints():
    mods = {}

    for path, dirs, files in os.walk("core/modules", topdown=False):
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

    for path, dirs, files in os.walk("modules", topdown=False):
        for fname in files:
            try:
                name, ext = os.path.splitext(fname)
                if ext == '.py' and not name == '__init__':
                    f, filename, descr = imp.find_module(name, [path])
                    mods[fname] = imp.load_module(name, f, filename, descr)
                    #print(getattr(mods[fname]))
                    app.register_blueprint(getattr(mods[fname], 'module'), url_prefix=f'/{mods[fname].module.name}')
                    print(Fore.GREEN + '[Module] ' + Style.RESET_ALL + 'Imported', mods[fname].module.name)
                    #globals()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(Fore.RED, '[ERROR]', path, name, e, exc_type, fname, exc_tb.tb_lineno, Style.RESET_ALL)

    return mods

mods = load_blueprints()
for f in mods:
    try:
        app.loadedModules += [mods[f].module.name]
        if mods[f].module.hasAdminPage == True:
            app.adminModules += [(mods[f].module.name, mods[f].module.moduleDescription, mods[f].module.version, mods[f].module.hasAdminPage)]
    except Exception as e:
        print(f, e)
print(Fore.GREEN + '[LoonaBilling] ' + Style.RESET_ALL + 'Loaded', len(mods), 'modules')

@app.route('/admin')
@hauth.login_required
def admin():
    return render_template('core/admin.html', tabs=app.adminModules, map=app.url_map, cpuUsage=int(psutil.cpu_percent()), ramUsage=int(psutil.virtual_memory().percent), storageUsage=int(psutil.disk_usage('/').percent))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', businessName=config.businessName), 404

if __name__ == '__main__':
    app.config['SERVER_NAME'] = config.domain
    if app.hasUpdate:
        print(Fore.GREEN + '[LoonaBilling] ' + Fore.YELLOW + '*** There is a new update! ***' + Style.RESET_ALL)
    print(Fore.GREEN + '[LoonaBilling] ' + Style.RESET_ALL + 'Ready to start')
    app.run(host=config.ip, port=config.port, debug=config.debug, ssl_context=config.ssl)
