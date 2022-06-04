from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
import config
module = Blueprint('module', __name__)

@module.route('/module')
@module.route('/module/<page>')
def show(page=None):
    return f'Page = {page}'

@module.route('/getConfig')
def getConfig():
    return config.configTest
