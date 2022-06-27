from flask import Blueprint, render_template, abort, request, current_app
from jinja2 import TemplateNotFound
import config
import os
from flask import *
from werkzeug.utils import secure_filename
from core.utils.auth import auth
import config

module = Blueprint('Search', __name__)
module.hasAdminPage = True
module.moduleDescription = 'Allows customers to search your site'
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

def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

@module.route('/search')
def searchPage():
    links = []
    for rule in current_app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            print(url)
            if request.args['search'] in str(url):
                if 'admin' not in url:
                    links.append((url, rule.endpoint))
    return render_template('core/Search/search.html', searches=links, search=request.args['search'], businessName=config.businessName)

#@module.route('/admin/{}'.format(module.name))
#@auth.login_required
#def adminPage():
#    return render_template('core/Mail/admin.html', businessName=config.businessName, moduleName=module.name, moduleDescription=module.moduleDescription)

#@module.route('/admin/{}/editSettings'.format(module.name))
#@auth.login_required
#def editSettings():
#    return render_template('core/Mail/adminEditSettings.html', businessName=config.businessName, moduleName=module.name, moduleDescription=module.moduleDescription)
