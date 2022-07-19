import requests
from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
from flask import *

module = Blueprint('httprequests', __name__)
module.hasAdminPage = False
module.moduleDescription = 'Automate simple http requests'
module.version = '1.0'

module.automation = [('sendRequest', {'url': 'str', 'data': 'str'})]

def sendRequest(url, data):
    try:
        x = requests.post(url, data=data, timeout=4)
        return x.text
    except Exception as e:
        print(e)
        return 0

# Soon
