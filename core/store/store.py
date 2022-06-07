from flask import Blueprint, render_template, abort
from flask import *
from jinja2 import TemplateNotFound
#import stripe
import config
import os
module = Blueprint('LoonaStore', __name__)
module.hasAdminPage = False

def cf(folder):
    try:
        os.mkdir(folder)
        print(f'[{module.name}] Created Folder: {folder}')
    except Exception as e:
        #print(e)
        pass

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
        category = request.args['category']
    if 'item' in request.args:
        item = request.args['item']
    return 'Welcome to the store!' #<br>{} | {}'.format(category, item) # Removed due to CWE-79 & CWE-116
