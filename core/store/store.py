from flask import Blueprint, render_template, abort
from flask import *
from jinja2 import TemplateNotFound
#import stripe
import config
import os
from werkzeug.utils import secure_filename

module = Blueprint('LoonaStore', __name__)
module.hasAdminPage = False
module.moduleDescription = 'The Core Store Module for LoonaBilling'
module.version = '1.2'

def cf(folder):
    try:
        os.mkdir(folder)
        print(f'[{module.name}] Created Folder: {folder}')
    except Exception as e:
        #print(e)
        return

def checks():
    try:
        import configs.store.config as storeConfig
    except:
        cf('configs/store')
        cf('configs/store/data')
        a = open('configs/store/config.py', 'w+').write('''# Core Module Config


''')
        try:
            import configs.store.config as storeConfig
            print("Store config was created. Please update the config located at configs/store/config.py")
        except:
            print('ERROR: STORE CONFIG NOT FOUND')

    cf('products')

checks()

@module.route('/store')
def store():
    category = ''
    item = ''
    if 'category' in request.args:
        category = secure_filename(request.args['category'])
    if 'item' in request.args:
        item = request.args['item']
    #if category == '':
    #    return str(os.listdir('products'))
    categories = []
    items = []
    for f in os.listdir('products/{}'.format(category)):
        if os.path.isdir(os.path.join('products/', category, f)):
            print('folder')
            categories += [f]
        if os.path.isfile(os.path.join('products/', category, f)):
            with open(os.path.join('products/', category, f)) as of:
                data = json.load(of)
                for p in data['Config']:
                    prc = list(p['price'])
                    prc.insert(-2, '.')
                    print(prc)
                    #print(list(p['price']).insert(-2, '.'))
                    items += [(p['title'], ''.join(prc), p['description'], f.split('.')[0], p['provider'])]

    return render_template('core/LoonaStore/index.html', businessName=config.businessName, categories=categories, items=items, category=category)
