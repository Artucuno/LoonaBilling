import logging
logging.basicConfig(level=logging.DEBUG)
import sys, os
import json
from flask import Flask
from flask import *
import stripe
import config
import importlib
import imp
from colorama import Fore, Back, Style
from colorama import init
from cryptography.fernet import Fernet

init()

app = Flask(__name__)
app.adminModules = []
def cf(folder):
    try:
        os.mkdir(folder)
        print(f'[LoonaBilling] Created Folder: {folder}')
    except Exception as e:
        #print(e)
        pass

def checks():
    cf('configs')
    cf('modules')
    cf('modules/user')
    cf('modules/admin')
    cf('core')
    cf('core/payments')
    cf('products')
    cf('logs')

checks()

def load_blueprints():
    """
    https://github.com/smartboyathome/Cheshire-Engine/blob/master/ScoringServer/utils.py
    """
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
print(app.url_map)
print(mods)
for f in mods:
    #print(f)
    if mods[f].module.hasAdminPage == True:
        app.adminModules += [mods[f].module.name]
    print(f, mods[f].module.name, mods[f].module.hasAdminPage)

@app.route('/')
def main():
    return render_template('core/index.html', aboutText=config.aboutText, businessName=config.businessName)

@app.route('/about')
def about():
    return render_template('core/about.html', aboutText=config.aboutText, businessName=config.businessName) # CHANGE TO ABOUT PAGE

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('core/contact.html', aboutText=config.aboutText, businessName=config.businessName) # CHANGE TO CONTACT PAGE

@app.route('/admin')
def admin():
    return render_template('core/admin.html', tabs=app.adminModules)

app.config['SERVER_NAME'] = config.domain
app.run(host=config.ip, port=config.port, debug=config.debug, ssl_context=config.ssl)
