from flask import Blueprint, render_template, abort
from flask import *
from jinja2 import TemplateNotFound
import config
import sys, os
from colorama import Fore, Back, Style
from colorama import init
import imp
import json
from werkzeug.utils import secure_filename
from core.utils.auth import hauth
from core.utils import files as fls
# TODO:
# Add automation API selection

module = Blueprint('Products', __name__)
module.hasAdminPage = True
module.moduleDescription = 'The Core Product Management Module for LoonaBilling'
module.version = '1.4'

def cf(folder):
    try:
        os.mkdir(folder)
        print(f'[{module.name}] Created Folder: {folder}')
    except Exception as e:
        #print(e)
        return

mods = {}
paypro = []
prodpro = []
for path, dirs, files in os.walk("core/modules/payments", topdown=False):
    for fname in files:
        try:
            name, ext = os.path.splitext(fname)
            if ext == '.py' and not name == '__init__':
                f, filename, descr = imp.find_module(name, [path])
                mods[fname] = imp.load_module(name, f, filename, descr)
                #print(getattr(mods[fname], 'module').name)
                paypro += [getattr(mods[fname], 'module')]
                prodpro += [(getattr(mods[fname], 'module'), fname)]
                print(Fore.GREEN + f'[{module.name}] ' + Style.RESET_ALL + 'Imported', mods[fname].module.name)
                #globals()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Fore.RED, '[ERROR]', path, name, e, exc_type, fname, exc_tb.tb_lineno, Style.RESET_ALL)

automods = {}
autopro = []

for path, dirs, files in os.walk("core/modules/automation", topdown=False):
    for fname in files:
        try:
            name, ext = os.path.splitext(fname)
            if ext == '.py' and not name == '__init__':
                f, filename, descr = imp.find_module(name, [path])
                automods[fname] = imp.load_module(name, f, filename, descr)
                #print(getattr(mods[fname], 'module').name)
                autopro += [(getattr(automods[fname], 'module').name, fls.getFuncts(automods[fname]))]
                print(Fore.GREEN + f'[{module.name}] ' + Style.RESET_ALL + 'Imported', automods[fname].module.name)
                #globals()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Fore.RED, '[ERROR]', path, name, e, exc_type, fname, exc_tb.tb_lineno, Style.RESET_ALL)

def checks():
    cf('products')
    cf('products/default')
    cf('static')
    cf('static/assets')
    cf('static/assets/prodimages')

checks()

@module.route('/admin/{}'.format(module.name))
@hauth.login_required
def adminPage():
    return render_template('core/LoonaProducts/admin.html', businessName=fls.getBranding()[0], moduleName=module.name, moduleDescription=module.moduleDescription)

@module.route('/admin/{}/createCategory'.format(module.name), methods=['GET', 'POST'])
@hauth.login_required
def createCategory():
    if request.method == 'POST':
        try:
            os.mkdir(os.path.join('products', secure_filename(request.form['category'].strip())))
        except Exception as e:
            print(e)
            return render_template('core/LoonaProducts/adminCreateCategory.html', msg='Category already exists', businessName=fls.getBranding()[0], moduleName=module.name, moduleDescription=module.moduleDescription)
        return render_template('core/LoonaProducts/adminCreateCategory.html', msg='Category created', businessName=fls.getBranding()[0], moduleName=module.name, moduleDescription=module.moduleDescription)
    return render_template('core/LoonaProducts/adminCreateCategory.html', businessName=fls.getBranding()[0], moduleName=module.name, moduleDescription=module.moduleDescription)

@module.route('/admin/{}/deleteCategory'.format(module.name), methods=['GET', 'POST'])
@hauth.login_required
def deleteCategory():
    if request.method == 'POST':
        try:
            if os.path.isdir():
                os.remove(os.path.join('products', secure_filename(request.form['category'].strip())))
        except Exception as e:
            print(e)
            return render_template('core/LoonaProducts/adminCreateCategory.html', msg="Category doesn't exists or access is denied", businessName=fls.getBranding()[0], moduleName=module.name, moduleDescription=module.moduleDescription)
        return render_template('core/LoonaProducts/adminCreateCategory.html', msg='Category deleted', businessName=fls.getBranding()[0], moduleName=module.name, moduleDescription=module.moduleDescription)
    return render_template('core/LoonaProducts/adminDeleteCategory.html', businessName=fls.getBranding()[0], moduleName=module.name, moduleDescription=module.moduleDescription)


@module.route('/admin/{}/manageProducts'.format(module.name), methods=['GET', 'POST'])
@hauth.login_required
def manageProducts():
    prods = []
    try:
        for f in mods:
            try:
                rgs = getattr(mods[f], 'getProducts')()
                #print(rgs)
                prods += [(getattr(mods[f], 'module').name, rgs)]
            except:
                print(f'[Payments] Unable to get products for {mods[f]}')
        return render_template('core/LoonaProducts/adminManageProducts.html', prods=prods)
    except Exception as e:
        print(e)
        return 'Unable to load'

@module.route('/admin/{}/createProduct'.format(module.name), methods=['GET', 'POST'])
@hauth.login_required
def createProduct():
    if request.method == 'POST':
        print(request.form)
        #print(request.files)
        description = ''
        image = None
        rgs = {}
        if 'description' in request.form:
            description = request.form['description']
        if 'title' not in request.form:
            return render_template('core/LoonaProducts/adminCreateProduct.html', categories=os.listdir('products'), msg='Title is missing', businessName=fls.getBranding()[0], moduleName=module.name, moduleDescription=module.moduleDescription)
        elif 'price' not in request.form:
            return render_template('core/LoonaProducts/adminCreateProduct.html', categories=os.listdir('products'), msg='Price is missing', businessName=fls.getBranding()[0], moduleName=module.name, moduleDescription=module.moduleDescription)
        elif 'automation' not in request.form:
            return render_template('core/LoonaProducts/adminCreateProduct.html', categories=os.listdir('products'), msg='Automation is missing (None or function)', businessName=fls.getBranding()[0], moduleName=module.name, moduleDescription=module.moduleDescription)
        else:
            itemID = len(os.listdir('products/{}'.format(secure_filename(request.form['category']))))
            if 'prodImage' in request.files:
                if request.files['prodImage'].filename != '':
                    image = 'static/assets/prodimages/{}.{}'.format(itemID, secure_filename(request.files['prodImage'].filename.split('.')[-1]))
                    request.files['prodImage'].save(image)
            price = request.form['price']
            if '.' not in request.form['price']:
                price = request.form['price'] + '00' # Stripe uses the 2 numbers on the end for cents
            else:
                if len(price.split('.')[1]) == 1:
                    price += '0'
                if len(price.split('.')[1]) > 2:
                    price = price.replace(price.split('.')[1], str(round(float(price.split('.')[1]), 2)))
            try:
                paytyp = request.form['paytype']
                print(paytyp)
                if paytyp in ['payment', 'subscription']:
                    paytype = paytyp
            except:
                paytype = 'payment'
            autom = None
            if request.form['automation'] != 'None':
                autom = request.form['automation']
            data = {}
            data['Config'] = []
            data['Config'].append({
            'title': request.form['title'],
            'description': description,
            'price': price.replace('.', ''),
            'automationtype': 'str',
            'automation': [autom, request.form['automationargs']],
            'image': image,
            'removed': False,
            'currency': request.form['currency'],
            'args': rgs,
            'type': paytype,
            'category': secure_filename(request.form['category']),
            'args': {}
            })
            for pro in prodpro:
                if 'createProduct' in pro[0].supportedActions:
                    a = getattr(mods[pro[1]], 'createProduct')(data)
                    print(a)
                    data['Config'][0]['args']['{}'.format(pro[0].name)] = {'prod': a['id'], 'price': a['default_price']}
            with open('products/{}/{}.json'.format(secure_filename(request.form['category']), itemID), 'w+') as of:
                json.dump(data, of)
            return render_template('core/LoonaProducts/adminCreateProduct.html', payments=paypro, categories=os.listdir('products'), msg=f'Created Product: {request.form["title"]}', businessName=fls.getBranding()[0], moduleName=module.name, moduleDescription=module.moduleDescription)
    return render_template('core/LoonaProducts/adminCreateProduct.html', payments=paypro, automation=autopro, categories=os.listdir('products'), businessName=fls.getBranding()[0], moduleName=module.name, moduleDescription=module.moduleDescription)
