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

init()

app = Flask(__name__)

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
            #print(fname)
            #if os.path.isdir(os.path.join(path, fname)) and os.path.exists(os.path.join(path, fname, '__init__.py')):
            #    f, filename, descr = imp.find_module(fname, [path])
            #    mods[fname] = imp.load_module(fname, f, filename, descr)
            #    app.register_blueprint(getattr(mods[fname], 'module'), url_prefix='/admin')
            try:
                name, ext = os.path.splitext(fname)
                if ext == '.py' and not name == '__init__':
                    f, filename, descr = imp.find_module(name, [path])
                    mods[fname] = imp.load_module(name, f, filename, descr)
                    app.register_blueprint(getattr(mods[fname], 'module'), url_prefix=f'/{name}')
                    print(Fore.GREEN + '[Module] ' + Style.RESET_ALL + 'Imported', mods[fname].module.name)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(path, name, e, exc_type, fname, exc_tb.tb_lineno)

    for path, dirs, files in os.walk("core", topdown=False):
        for fname in files:
            #print(fname)
            #if os.path.isdir(os.path.join(path, fname)) and os.path.exists(os.path.join(path, fname, '__init__.py')):
            #    f, filename, descr = imp.find_module(fname, [path])
            #    mods[fname] = imp.load_module(fname, f, filename, descr)
            #    app.register_blueprint(getattr(mods[fname], 'module'), url_prefix='/admin')
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
                print(path, name, e, exc_type, fname, exc_tb.tb_lineno)


load_blueprints()
print(app.url_map)

@app.route('/')
def main():
    return render_template('core/index.html', businessName=config.businessName)

@app.route('/about')
def about():
    return render_template('core/index.html', businessName=config.businessName) # CHANGE TO ABOUT PAGE

@app.route('/contact')
def contact():
    return render_template('core/index.html', businessName=config.businessName) # CHANGE TO CONTACT PAGE

@app.route('/admin')
def admin():
    return 'admin'

app.run(host='0.0.0.0', port=80, debug=True)
