from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
import config
from werkzeug.utils import secure_filename
from core.utils.auth import hauth
from core.utils import files
import sys, os
from colorama import Fore, Back, Style
from colorama import init
import imp

module = Blueprint('Payments', __name__)
module.hasAdminPage = False
module.moduleDescription = 'Payment Management'
module.version = '1.0'

def checks():
    try:
        for f in os.listdir('data/cart'):
            try:
                os.remove(f'data/cart/{f}')
            except:
                print(f'[{module.name}] Unable to remove {f} state')
    except:
        print()

checks()

mods = {}
paypro = []
for path, dirs, file in os.walk("core/modules/payments", topdown=False):
    for fname in file:
        try:
            name, ext = os.path.splitext(fname)
            if ext == '.py' and not name == '__init__':
                f, filename, descr = imp.find_module(name, [path])
                mods[fname] = imp.load_module(name, f, filename, descr)
                #print(getattr(mods[fname], 'module').name)
                paypro += [getattr(mods[fname], 'module')]
                print(Fore.GREEN + f'[{module.name}] ' + Style.RESET_ALL + 'Imported', mods[fname].module.name)
                #globals()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Fore.RED, '[ERROR]', path, name, e, exc_type, fname, exc_tb.tb_lineno, Style.RESET_ALL)

@module.route("/success")
def success():
    return render_template('core/Payments/paymentSucess.html', businessName=files.getBranding()[0])

@module.route("/cancelled")
def cancelled():
    return render_template('core/Payments/paymentCancelled.html', businessName=files.getBranding()[0])
