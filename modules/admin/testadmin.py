from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
import config
module = Blueprint('module', __name__)
module.hasAdminPage = False

@module.route('/module')
@module.route('/module/<page>')
def show(page=None):
    return f'Page = {page}'
