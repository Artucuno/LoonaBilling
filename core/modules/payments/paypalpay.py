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
module.version = '2.0'
module.supportedMethods = ['payment']
module.supportedActions = []

# https://developer.paypal.com/developer/applications
# https://developer.paypal.com/developer/accounts

payconfig = PayPalConfig(API_USERNAME = "xxxxxxx.business.example.com",
                      API_PASSWORD = "xxxxxxxx",
                      API_SIGNATURE = "xxxxxxxxxxxxxxx",
                      DEBUG_LEVEL=0)

interface = paypal.PayPalInterface(config=payconfig)

def getCart(token):
    token = secure_filename(token)
    if os.path.isfile(f'data/cart/{token}'):
        with open(f'data/cart/{token}') as of:
            data = json.load(of)
            return data['Config'][0], {}
    else:
        return False, {}

def getItem(category, item):
    category = secure_filename(category).replace('products_', '')
    item = secure_filename(item)
    with open(f'products/{category}/{item}.json') as of:
        data = json.load(of)
        return data['Config'][0]

@module.route(f'/{module.name}/startSession')
def payment():
    return redirect(url_for('LoonaStore.checkout'))
    # LOOKING FOR CONTRIBUTORS TO HELP MAKE THE PAYPAL MODULE


    user = json.loads(json.dumps(auth.isAuth(session['user'])))
    if user != False:
        for p in user['Config']:
            try:
                paytype = request.args['type']
            except:
                return render_template('error.html', msg='Unspecified Payment Type')
            if paytype == 'buy':
                try:
                    category = request.args['category']
                    item = request.args['item']
                except:
                    return render_template('error.html', msg='Category or Item Unspecified')
            elif paytype == 'cart':
                try:
                    cartid = request.args['cartid']
                except:
                    return render_template('error.html', msg='Cart ID Unspecified')
            else:
                return ''
            mode = 'payment'
            modes = ['payment']
            try:
                md = request.args['mode']
                if md not in modes:
                    return 'Invalid mode'
                mode = md
            except Exception as e:
                print(e)
                mode = 'payment'
            items, mtd = getCart(cartid)
            #print(items)
            if items == False:
                return 'No items, try restarting your session'
            price = 0
            for f in items['cart']:
                #for ff in f0['cart']:
                #print(items)
                #print(f['cart'])
                i = getItem(f['category'], f['item'])
                price += int(i['price'])
            prc = list(str(price))
            prc.insert(-2, '.')
            kw = {
                'amt': ''.join(prc),
                'currencycode': 'USD',
                'returnurl': url_for('Payments.success', _external=True),
                'cancelurl': url_for('Payments.cancelled', _external=True),
                'paymentaction': 'Sale'
            }
            setexp_response = interface.set_express_checkout(**kw)
            print(setexp_response.token)
            return redirect(interface.generate_express_checkout_redirect_url(setexp_response.token))

@module.route(f'/{module.name}/webhook', methods=['GET', 'POST'])
def webhook():
    print(request.headers)
    event = json.loads(request.data)
    print(event)
    if event['event_type'] == 'CHECKOUT.ORDER.COMPLETED':
        print(event['resource']['status'])
    return jsonify(success=True)
