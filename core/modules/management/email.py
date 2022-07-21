# Need to finish
from flask import Blueprint, render_template, abort
from flask import *
from jinja2 import TemplateNotFound
import config
import os
from werkzeug.utils import secure_filename
from core.utils.auth import hauth
from core.utils import files
import json
from uuid import getnode
from cryptography.fernet import Fernet

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
    if not os.path.isfile('configs/mail/config.json'):
        data = {}
        data['Config'] = []
        data['Config'].append({
        'hostname': '',
        'username': '',
        'password': '',
        'port': 587,
        'tsslreqired': False
        })
        with open('configs/mail/config.json', 'w+') as of:
            json.dump(data, of)

checks()

@module.route('/admin/{}'.format(module.name))
@hauth.login_required
def adminPage():
    return render_template('core/Mail/admin.html', businessName=files.getBranding()[0], moduleName=module.name, moduleDescription=module.moduleDescription)

@module.route('/admin/{}/editSettings'.format(module.name), methods=['GET', 'POST'])
@hauth.login_required
def editSettings():
    if request.method == 'POST':
        print(request.form)
        files.updateJSON('configs/mail/config.json', 'hostname', request.form['mailServer'])
        files.updateJSON('configs/mail/config.json', 'username', request.form['mailName'])
        files.updateJSON('configs/mail/config.json', 'password', Fernet(getnode().encode()).encrypt(request.form['mailPassword'].encode()).decode())
        files.updateJSON('configs/mail/config.json', 'port', request.form['port'])
        files.updateJSON('configs/mail/config.json', 'tsslreqired', 'req' in request.form)
    return render_template('core/Mail/adminEditSettings.html', businessName=files.getBranding()[0], moduleName=module.name, moduleDescription=module.moduleDescription)
