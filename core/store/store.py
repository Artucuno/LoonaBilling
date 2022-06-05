from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
#import stripe
import config
import os
module = Blueprint('LoonaStore', __name__)

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
@module.route('/store/')
@module.route('/store/<category>')
@module.route('/store/<category>/<item>')
def store(category=None, item=None):
    return 'Welcome to the store!<br>{} | {}'.format(category, item)
