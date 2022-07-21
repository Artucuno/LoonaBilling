# LoonaBilling
# Made by Artucuno (https://github.com/Artucuno)


import time
import logging
lf = True
if lf == True:
    try:
        logging.basicConfig(filename='logs/'+str(time.time())+'.log',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)
    except Exception as e:
        print('Unable to start logging', e)
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
from werkzeug.utils import secure_filename
from core.utils.auth import hauth
from core.utils import files
from core.utils import network
from git import Repo
import urllib.parse

print(os.getpid()) # Checking resource usage for pid
tprint("LoonaBilling")
init()

app = Flask(__name__)
app.adminModules = []
app.loadedModules = []
app.version = '1.8.1'
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
    cf('configs/core')
    cf('configs/core/branding')
    if not os.path.isfile('configs/core/branding/branding.json'):
        br = {}
        br['Config'] = []
        br['Config'].append({
        'businessName': 'Loona',
        'aboutText': 'A WIP Opensource WHMCS alternative',
        'logo': None,
        'favicon': None
        })
        with open('configs/core/branding/branding.json', 'w+') as of:
            json.dump(br, of)
    cf('configs/core/modules')
    cf('modules')
    cf('core')
    cf('core/modules')
    cf('core/modules/automation')
    cf('core/modules/management')
    cf('core/modules/pages')
    cf('core/modules/payments')
    cf('core/modules/store')
    cf('core/modules/other')
    cf('core/utils')
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
        print("Welcome to LoonaBilling! To get started, please enter an admin password to use for login.")
        adPass = getpass.getpass('Enter new admin password >>> ')
        key = encKey(adPass)
        #input(key)
        with open('setup', 'wb') as of:
            of.write(key)
        of.close()
        print('''
=================
Welcome to LoonaBilling! (v{})

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

    for path, dirs, file in os.walk("core/modules", topdown=False):
        for fname in file:
            try:
                name, ext = os.path.splitext(fname)
                if ext == '.py' and not name == '__init__':
                    f, filename, descr = imp.find_module(name, [path])
                    mods[fname] = imp.load_module(name, f, filename, descr)
                    if os.path.isfile('configs/core/modules/{}'.format(getattr(mods[fname], 'module').name)):
                        if files.readJSONVar('configs/core/modules/{}'.format(getattr(mods[fname], 'module').name), 'enabled') == True:
                            app.register_blueprint(getattr(mods[fname], 'module'))#, url_prefix=f'/{name}')
                    else:
                        data = {}
                        data['Config'] = []
                        data['Config'].append({
                        'enabled': True
                        })
                        with open('configs/core/modules/{}'.format(getattr(mods[fname], 'module').name), 'w+') as of:
                            json.dump(data, of)
                        app.register_blueprint(getattr(mods[fname], 'module'))
                    print(Fore.GREEN + '[Core] ' + Style.RESET_ALL + 'Imported', mods[fname].module.name)
            except Exception as e:
                try:
                    del mods[fname]
                except:
                    print(Fore.RED, f'[ERROR] Unable to remove {fname} from list', Style.RESET_ALL)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(Fore.RED, '[ERROR]', path, name, e, exc_type, fname, exc_tb.tb_lineno, Style.RESET_ALL)

    for path, dirs, file in os.walk("modules", topdown=False):
        for fname in file:
            try:
                name, ext = os.path.splitext(fname)
                if ext == '.py' and not name == '__init__':
                    f, filename, descr = imp.find_module(name, [path])
                    mods[fname] = imp.load_module(name, f, filename, descr)
                    #print(getattr(mods[fname]))
                    if os.path.isfile('configs/core/modules/{}'.format(getattr(mods[fname], 'module').name)):
                        if files.readJSONVar('configs/core/modules/{}'.format(getattr(mods[fname], 'module').name), 'enabled') == True:
                            app.register_blueprint(getattr(mods[fname], 'module'))#, url_prefix=f'/{name}')
                    else:
                        data = {}
                        data['Config'] = []
                        data['Config'].append({
                        'enabled': True
                        })
                        with open('configs/core/modules/{}'.format(getattr(mods[fname], 'module').name), 'w+') as of:
                            json.dump(data, of)
                        app.register_blueprint(getattr(mods[fname], 'module'))
                    print(Fore.GREEN + '[Module] ' + Style.RESET_ALL + 'Imported', mods[fname].module.name)
                    #globals()
            except Exception as e:
                try:
                    del mods[fname]
                except:
                    print(Fore.RED, f'[ERROR] Unable to remove {fname} from list', Style.RESET_ALL)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(Fore.RED, '[ERROR]', path, name, e, exc_type, fname, exc_tb.tb_lineno, Style.RESET_ALL)

    return mods

def loadModules():
    app.mods = load_blueprints()
    for f in app.mods:
        try:
            app.loadedModules += [app.mods[f].module.name]
            if app.mods[f].module.hasAdminPage == True:
                app.adminModules += [(app.mods[f].module.name, app.mods[f].module.moduleDescription, app.mods[f].module.version, app.mods[f].module.hasAdminPage)]
        except Exception as e:
            print(f, e)
    print(Fore.GREEN + '[LoonaBilling] ' + Style.RESET_ALL + 'Loaded', len(app.loadedModules), 'modules')

loadModules()

@app.route('/admin')
@hauth.login_required
def admin():
    return render_template('core/admin.html', app=app, cpuUsage=int(psutil.cpu_percent()), ramUsage=int(psutil.virtual_memory().percent), storageUsage=int(psutil.disk_usage('/').percent))

@app.route('/admin/branding', methods=['GET', 'POST'])
@hauth.login_required
def adminBranding():
    if request.method == 'POST':
        files.updateJSON('configs/branding/branding.json', 'businessName', request.form['businessName'])
        files.updateJSON('configs/branding/branding.json', 'aboutText', request.form['aboutText'])
    return render_template('core/adminBranding.html', config=files.getBranding(), app=app)

@app.route('/admin/update', methods=['GET', 'POST'])
@hauth.login_required
def adminUpdate():
    if request.method == 'POST':
        print(request.form)
        if 'update' in request.form:
            repo = git.Repo("")
            o = repo.remotes.origin
            o.pull()
        if 'checkUpdate' in request.form:
            try:
                x = requests.get('https://raw.githubusercontent.com/Loona-cc/LoonaBilling/main/version', timeout=3)
                if x.text.strip() != app.version:
                    app.hasUpdate = True
                else:
                    print('You are on the latest version!')
            except Exception as e:
                print('Unable to get latest version: {}'.format(e))
        return redirect(url_for('adminUpdate'))
    return render_template('core/adminUpdate.html', app=app, changelog=network.getChangelog())

@app.route('/admin/modules', methods=['GET', 'POST'])
@hauth.login_required
def adminModules():
    if request.method == 'POST':
        if 'repoAuthor' and 'repoName' in request.form:
            try:
                x = requests.get('https://raw.githubusercontent.com/{}/{}/main/manifest.json'.format(request.form['repoAuthor'], request.form['repoName']), timeout=3)
                data = json.loads(x.text)
                print(data)
                Repo.clone_from('https://github.com/{}/{}.git'.format(request.form['repoAuthor'], request.form['repoName']), 'modules/{}'.format(request.form['repoName']))
                return 'Module Installed, please restart LoonaBilling.'
            except Exception as e:
                print(e)
                return 'Error when downloading module, check console.'
            #Repo.clone_from(request.form['gitRepo'], repo_dir)
        try:
            for f in request.form:
                #print(f, app.loadedModules)
                if f in app.loadedModules:
                    files.endisModule(f)
        except Exception as e:
            print(e)

            return redirect(url_for('adminModules'))
    #for f in list(app.url_map.iter_rules()):
    #    print(f, f.endpoint)
    return render_template('core/adminModules.html', app=app, moduleEnabled=files.moduleEnabled)

@app.route('/admin/filemanager')
@hauth.login_required
def adminFilemanager():
    if not config.filemanagerEnabled:
        return 'Filemanager is not enabled'
    #for f in list(app.url_map.iter_rules()):
    #    print(f, f.endpoint)
    dirs = []
    files = []
    dir = ''
    if 'dir' in request.args:
        dir = request.args['dir']
    for f in os.listdir(os.path.join('templates', dir)):
        if os.path.isdir(os.path.join('templates', dir, f)):
            dirs += [(os.path.join(dir, f), f)]
        if os.path.isfile(os.path.join('templates', dir, f)):
            if os.path.join('templates', dir, f).endswith('.html'):
                files += [(os.path.join(dir, f), f)]

    return render_template('core/adminFilemanager.html', app=app, dirs=dirs, files=files)

@app.route('/admin/themes', methods=["GET", "POST"])
@hauth.login_required
def adminThemes():
    return render_template('core/adminThemes.html', app=app)

@app.route('/admin/filemanager/edit', methods=["GET", "POST"])
@hauth.login_required
def adminFilemanagerEdit():
    if not config.filemanagerEnabled:
        return 'Filemanager is not enabled'
    if 'file' not in request.args:
        return redirect(url_for('adminFilemanager'))
    if 'admin' in request.args['file']:
        return 'Due to security reasons, admin templates can not be edited.'
    if request.method == 'POST':
        #print(repr(request.form['content']))
        with open(os.path.join('templates', request.args['file']), 'w+') as of:
            of.write(request.form['content'].replace('\r', ''))
    if os.path.isfile(os.path.join('templates', request.args['file'])):
        with open(os.path.join('templates', request.args['file']), 'r') as of:
            return render_template('core/adminEditFile.html', app=app, filename=request.args['file'], filelocation=request.args['file'], content=of.read())
    else:
        return render_template('error.html', businessName=files.getBranding()[0], msg='File does not exist!')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', businessName=files.getBranding()[0]), 404

if __name__ == '__main__':
    app.config['SERVER_NAME'] = config.domain
    if app.hasUpdate:
        print(Fore.GREEN + '[LoonaBilling] ' + Fore.YELLOW + '*** There is a new update! ***' + Style.RESET_ALL)
    print(Fore.GREEN + '[LoonaBilling] ' + Style.RESET_ALL + f'Ready to start on {config.ip}/{config.domain}')
    app.run(host=config.ip, port=config.port, debug=config.debug, ssl_context=config.ssl)
