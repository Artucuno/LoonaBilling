from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
#import stripe
import config
import os
module = Blueprint('LoonaProducts', __name__)
module.hasAdminPage = True

def cf(folder):
    try:
        os.mkdir(folder)
        print(f'[{module.name}] Created Folder: {folder}')
    except Exception as e:
        #print(e)
        pass

def checks():
    cf('products')

checks()

@module.route('/admin/{}'.format(module.name))
def adminPage():
    return render_template('core/LoonaProducts/admin.html', businessName=config.businessName)
