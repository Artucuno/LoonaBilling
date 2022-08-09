from flask import Blueprint, render_template, abort
from flask import *
from jinja2 import TemplateNotFound
#import stripe
import config
import sys, os
from werkzeug.utils import secure_filename
from core.utils import files
from colorama import Fore, Back, Style
from colorama import init
from core.utils import auth
import imp

module = Blueprint('LoonaStore', __name__)
module.hasAdminPage = False
module.moduleDescription = 'The Core Store Module for LoonaBilling'
module.version = '1.3'

def cf(folder):
    try:
        os.mkdir(folder)
        print(f'[{module.name}] Created Folder: {folder}')
    except Exception as e:
        #print(e)
        return

def checks():
    cf('products')
    cf('data')
    cf('data/cart')

checks()

mods = {}
paypro = []
for path, dirs, file in os.walk("core/modules/payments", topdown=False):
    for fname in file:
        try:
            name, ext = os.path.splitext(fname)
            if ext == '.py' and not name == '__init__':
                f, filename, descr = imp.find_module(name, [path])
                mods[fname] = imp.load_module(name, f, filename, descr)
                #print(getattr(mods[fname], 'module').name)
                paypro += [getattr(mods[fname], 'module')]
                print(Fore.GREEN + f'[{module.name}] ' + Style.RESET_ALL + 'Imported', mods[fname].module.name)
                #globals()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Fore.RED, '[ERROR]', path, name, e, exc_type, fname, exc_tb.tb_lineno, Style.RESET_ALL)

def getProduct(category, item):
    try:
        with open(f'products/{category}/{item}.json') as of:
            data = json.load(of)
            return data
    except Exception as e:
        print(e)
        return 'Error'

def parsePrice(price):
    prc = list(price)
    prc.insert(-2, '.')
    return ''.join(prc)

@module.route('/store', methods=['GET', 'POST'])
def store():
    if not 'cart' in session:
        session['cart'] = []
    category = ''
    item = ''
    if 'category' in request.args:
        category = secure_filename(request.args['category'])
    if 'item' in request.args:
        item = request.args['item']
    if request.method == 'POST':
        for f in request.form:
            print(f)
            try:
                x = f.split('-')
            except:
                return redirect(url_for('LoonaStore.store'))
            if x[0] == 'addcart':
                session['cart'] += [{'category': x[1], 'item': x[2]}]
            if x[0] == 'buynow':
                session['cart'] = [{'category': x[1], 'item': x[2]}]
                return redirect(url_for('LoonaStore.checkout'))
    categories = []
    items = []
    #if category == '':
    #    category = 'default'
    for f in os.listdir('products'):
        if os.path.isdir(f'products/{f}'):
            categories += [f]
    for f in os.listdir(f'products/{category}'):
        #if os.path.isdir(os.path.join('products/', category, f)):
            #print('folder')
        #    categories += [f]
        if os.path.isfile(os.path.join('products/', category, f)):
            with open(os.path.join('products/', category, f)) as of:
                data = json.load(of)
                for p in data['Config']:
                    prc = list(p['price'])
                    prc.insert(-2, '.')
                    #print(prc)
                    items += [(p['title'], ''.join(prc), p['description'], f.split('.')[0], p['type'], p['image'], p['currency'])]
    return render_template('core/LoonaStore/index.html', businessName=files.getBranding()[0], categories=categories, items=items, category=category)

@module.route('/cart', methods=['GET', 'POST'])
def cart():
    if not 'cart' in session:
        session['cart'] = []
    if request.method == 'POST':
        for f in request.form:
            try:
                x = f.split('-')
            except:
                return ''
            if x[0] == 'remove':
                #del session['cart'][int(x[1])-1]
                a = session['cart']
                del a[int(x[1])-1]
                session['cart'] = a
                print(session['cart'])
        return redirect(url_for('LoonaStore.cart'))
    return render_template('core/LoonaStore/cart.html', parsePrice=parsePrice, getProduct=getProduct, businessName=files.getBranding()[0])

@module.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if not 'cart' in session:
        session['cart'] = []
    prc = 0
    print(session['cart'])
    for f in session['cart']:
        print(f)
        a = getProduct(f['category'], f['item'])['Config'][0]
        prc += int(a['price'])
    pros = []
    for q in mods:
        pros += [getattr(mods[q], 'module').name]
    print(pros)
    if request.method == 'POST':
        print(request.form)
        for qp in request.form:
            try:
                x = qp.split('-')
            except:
                return 'Unable to checkout'
            if x[0] == 'payment':
                if x[1] in pros:
                    print('a')
                    carttoken = auth.genKey('data/cart')
                    data = {}
                    data['Config'] = []
                    data['Config'].append({
                    'provider': x[1],
                    'price': prc,
                    'cart': session['cart'],
                    'token': carttoken,
                    })
                    with open('data/cart/{}'.format(carttoken), 'w+') as of:
                        json.dump(data, of)
                    return redirect(url_for(f'{x[1]}.payment', cartid=carttoken, type='cart'))
                else:
                    return 'invalid provider'
            else:
                return 'p'
    return render_template('core/LoonaStore/checkout.html', paypros=pros, prc=parsePrice(str(prc)), businessName=files.getBranding()[0])
