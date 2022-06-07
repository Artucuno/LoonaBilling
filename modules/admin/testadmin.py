from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
import config
module = Blueprint('module', __name__)
module.hasAdminPage = False

@module.route('/testadmin')
def show():
    return 'Test admin'
