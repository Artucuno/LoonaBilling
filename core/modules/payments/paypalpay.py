from flask import Blueprint, render_template, abort
from flask import *
from jinja2 import TemplateNotFound
import paypal
import config
import os
from werkzeug.utils import secure_filename
from core.utils.auth import hauth
from core.utils import files
from core.utils import auth
from paypal import PayPalConfig
from paypal import PayPalInterface

module = Blueprint('PayPal', __name__)
module.hasAdminPage = True
module.moduleDescription = ''
module.version = '1.0'

# https://developer.paypal.com/developer/applications
# https://developer.paypal.com/developer/accounts

payconfig = PayPalConfig(API_USERNAME = "xxxxxx.business.example.com",
                      API_PASSWORD = "xxxxxx",
                      API_SIGNATURE = "xxxxxx",
                      DEBUG_LEVEL=0)

interface = paypal.PayPalInterface(config=payconfig)

@module.route(f'/{module.name}/startSession')
def paypal_redirect():
    ritem = secure_filename(request.args['item'])
    rcate = secure_filename(request.args['category'])
    if 'category' not in request.args:
        return render_template('error.html', msg='No category was specified.', businessName=files.getBranding()[0])
    if 'item' not in request.args:
        return render_template('error.html', msg='No item ID was specified.', businessName=files.getBranding()[0])
    if os.path.isdir('products/{}'.format(rcate)):#, request.args['item'])):
        with open('products/{}/{}.json'.format(rcate, ritem)) as of:
            data = json.load(of)
            for p in data['Config']:
                prc = list(p['price'])
                prc.insert(-2, '.')
                kw = {
                    'amt': ''.join(prc),
                    'currencycode': p['currency'],
                    'returnurl': url_for('PayPal.success', _external=True),
                    'cancelurl': url_for('PayPal.cancelled', _external=True),
                    'paymentaction': 'Sale'
                }
                setexp_response = interface.set_express_checkout(**kw)
                return redirect(interface.generate_express_checkout_redirect_url(setexp_response.token))

@module.route("/paypal/success")
def success():
    getexp_response = interface.get_express_checkout_details(token=request.args.get('token', ''))
    # Send email after purchase. Check checkout session a['email']
    #sendMail(None, None)
    #print(getexp_response)
    return render_template('core/Stripe/paymentSucess.html', businessName=files.getBranding()[0])

@module.route("/paypal/cancelled")
def cancelled():
    return render_template('core/Stripe/paymentCancelled.html', businessName=files.getBranding()[0])
