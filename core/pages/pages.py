from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
import config
import os
module = Blueprint('Pages', __name__)
module.hasAdminPage = True
module.moduleDescription = 'Simple pages for LoonaBilling'

def cf(folder):
    try:
        os.mkdir(folder)
        print(f'[{module.name}] Created Folder: {folder}')
    except Exception as e:
        #print(e)
        pass

def checks():
    cf('templates')
    cf('templates/core')

checks()

@module.route('/')
def main():
    return render_template('core/index.html', aboutText=config.aboutText, businessName=config.businessName)

@module.route('/about')
def about():
    return render_template('core/about.html', aboutText=config.aboutText, businessName=config.businessName) # CHANGE TO ABOUT PAGE

@module.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('core/contact.html', aboutText=config.aboutText, businessName=config.businessName) # CHANGE TO CONTACT PAGE
