from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
import config
module = Blueprint('TestAdmin', __name__)
module.hasAdminPage = False
module.moduleDescription = 'A test module'

@module.route('/testadmin')
def show():
    return 'Test admin'
