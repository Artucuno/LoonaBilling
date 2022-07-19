from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
import config
import os

from core.utils import files

module = Blueprint('Pages', __name__)
module.hasAdminPage = False # Will be added back soon
module.moduleDescription = 'Simple pages for LoonaBilling'
module.version = '1.1'

def cf(folder):
    try:
        os.mkdir(folder)
        print(f'[{module.name}] Created Folder: {folder}')
    except Exception as e:
        #print(e)
        return

def checks():
    cf('templates')
    cf('templates/core')

checks()

@module.route('/')
def main():
    return render_template('core/index.html', aboutText=files.getBranding()[1], businessName=files.getBranding()[0])

@module.route('/about')
def about():
    return render_template('core/about.html', aboutText=files.getBranding()[1], businessName=files.getBranding()[0])

@module.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('core/contact.html', aboutText=files.getBranding()[1], businessName=files.getBranding()[0])
