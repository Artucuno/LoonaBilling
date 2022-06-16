from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
import config
module = Blueprint('TestUser', __name__)
module.hasAdminPage = False
module.moduleDescription = 'A test module'
module.version = '1.1'

@module.route('/testuser')
def show():
    return 'Test user'
