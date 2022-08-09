import requests
from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
from flask import *

module = Blueprint('httprequests', __name__)
module.hasAdminPage = False
module.moduleDescription = 'Automate simple http requests'
module.version = '1.1'
module.methods = dir()

module.automation = [('sendRequest', {'url': 'str', 'data': 'str'})]

def test(xee, eee):
    pass

def sendRequest(dta):
    print('**********', dta)
    url = dta[0]
    data = dta[1]
    try:
        timeout = dta[2]
    except:
        timeout = 4
    print(f'Sending data [{url}] ({data})')
    try:
        x = requests.post(url, data=data, timeout=timeout)
        print(x.text)
        return x.text
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(e, exc_type, fname, exc_tb.tb_lineno)
        return {'success': False, 'error': e}

# Soon
