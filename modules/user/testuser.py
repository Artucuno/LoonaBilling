from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
import config
module = Blueprint('moduleuser', __name__)
module.hasAdminPage = False

@module.route('/testuser')
def show():
    return 'Test user'
