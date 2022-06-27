# Need to finish
from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
import config
import os
from werkzeug.utils import secure_filename
from core.utils.auth import auth

module = Blueprint('Mail', __name__)
module.hasAdminPage = True
module.moduleDescription = 'Manage email settings'
module.version = '1.0'

def cf(folder):
    try:
        os.mkdir(folder)
        print(f'[{module.name}] Created Folder: {folder}')
    except Exception as e:
        #print(e)
        return

def checks():
    cf('configs')
    cf('configs/mail')

checks()

@module.route('/admin/{}'.format(module.name))
@auth.login_required
def adminPage():
    return render_template('core/Mail/admin.html', businessName=config.businessName, moduleName=module.name, moduleDescription=module.moduleDescription)

@module.route('/admin/{}/editSettings'.format(module.name))
@auth.login_required
def editSettings():
    return render_template('core/Mail/adminEditSettings.html', businessName=config.businessName, moduleName=module.name, moduleDescription=module.moduleDescription)
