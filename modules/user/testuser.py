from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
import config
module = Blueprint('moduleuser', __name__)
module.hasAdminPage = False

@module.route('/moduleuser')
@module.route('/moduleuser/<page>')
def show(page=None):
    return f'Page = {page}'
