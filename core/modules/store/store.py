from flask import Blueprint, render_template, abort
from flask import *
from jinja2 import TemplateNotFound
#import stripe
import config
import os
from werkzeug.utils import secure_filename
from core.utils import files

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

checks()

@module.route('/store')
def store():
    category = ''
    item = ''
    if 'category' in request.args:
        category = secure_filename(request.args['category'])
    if 'item' in request.args:
        item = request.args['item']
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
                    items += [(p['title'], ''.join(prc), p['description'], f.split('.')[0], p['provider'], p['image'])]

    return render_template('core/LoonaStore/index.html', businessName=files.getBranding()[0], categories=categories, items=items, category=category)
