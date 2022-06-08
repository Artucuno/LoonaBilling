from flask import Blueprint, render_template, abort
from flask import *
from jinja2 import TemplateNotFound
import stripe
import config
import sys, os
from colorama import Fore, Back, Style
from colorama import init
import imp
import json
module = Blueprint('Loona Products', __name__)
module.hasAdminPage = True
module.moduleDescription = 'The Core Product Management Module for LoonaBilling'
module.version = '1.1'

def cf(folder):
    try:
        os.mkdir(folder)
        print(f'[{module.name}] Created Folder: {folder}')
    except Exception as e:
        #print(e)
        pass
mods = {}
for path, dirs, files in os.walk("core/payments", topdown=False):
    for fname in files:
        try:
            name, ext = os.path.splitext(fname)
            if ext == '.py' and not name == '__init__':
                f, filename, descr = imp.find_module(name, [path])
                mods[fname] = imp.load_module(name, f, filename, descr)
                #print(getattr(mods[fname]))
                print(Fore.GREEN + '[Product Module] ' + Style.RESET_ALL + 'Imported', mods[fname].module.name)
                #globals()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Fore.RED, '[ERROR]', path, name, e, exc_type, fname, exc_tb.tb_lineno, Style.RESET_ALL)

def checks():
    cf('products')
    cf('products/default')

checks()

@module.route('/admin/{}'.format(module.name))
def adminPage():
    return render_template('core/LoonaProducts/admin.html', businessName=config.businessName, moduleName=module.name, moduleDescription=module.moduleDescription)

@module.route('/admin/{}/createProduct'.format(module.name), methods=['GET', 'POST'])
def createProduct():
    if request.method == 'POST':
        print(request.form)
        description = ''
        if 'description' in request.form:
            description = request.form['description']
        if 'title' not in request.form:
            return render_template('core/LoonaProducts/adminCreateProduct.html', categories=os.listdir('products'), msg='Title is missing', businessName=config.businessName, moduleName=module.name, moduleDescription=module.moduleDescription)
        elif 'price' not in request.form:
            return render_template('core/LoonaProducts/adminCreateProduct.html', categories=os.listdir('products'), msg='Price is missing', businessName=config.businessName, moduleName=module.name, moduleDescription=module.moduleDescription)
        else:
            data = {}
            data['Config'] = []
            data['Config'].append({
            'title': request.form['title'],
            'description': description,
            'price': request.form['price'],
            'automation': None
            })
            with open('products/{}/{}.json'.format(request.form['category'], len(os.listdir('products/{}'.format(request.form['category'])))), 'w+') as of:
                json.dump(data, of)
            return render_template('core/LoonaProducts/adminCreateProduct.html', categories=os.listdir('products'), msg=f'Created Product: {request.fprm["title"]}', businessName=config.businessName, moduleName=module.name, moduleDescription=module.moduleDescription)
    return render_template('core/LoonaProducts/adminCreateProduct.html', categories=os.listdir('products'), businessName=config.businessName, moduleName=module.name, moduleDescription=module.moduleDescription)
