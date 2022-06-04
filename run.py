import sys, os
import json
from flask import Flask
from flask import *
import stripe
import config
import importlib
import imp

stripe.api_version = '2020-08-27'
stripe.api_key = ''
domain_url = "http://localhost/"
app = Flask(__name__)

def load_blueprints():
    """
        This code looks for any modules or packages in the given directory, loads them
        and then registers a blueprint - blueprints must be created with the name 'module'
        Implemented directory scan

        Bulk of the code taken from:
            https://github.com/smartboyathome/Cheshire-Engine/blob/master/ScoringServer/utils.py
    """

    mods = {}
    path = 'modules/admin'
    dir_list = os.listdir(path)

    for fname in dir_list:
        if os.path.isdir(os.path.join(path, fname)) and os.path.exists(os.path.join(path, fname, '__init__.py')):
            f, filename, descr = imp.find_module(fname, [path])
            mods[fname] = imp.load_module(fname, f, filename, descr)
            app.register_blueprint(getattr(mods[fname], 'module'), url_prefix='/admin')
        elif os.path.isfile(os.path.join(path, fname)):
            name, ext = os.path.splitext(fname)
            if ext == '.py' and not name == '__init__':
                f, filename, descr = imp.find_module(name, [path])
                mods[fname] = imp.load_module(name, f, filename, descr)
                app.register_blueprint(getattr(mods[fname], 'module'), url_prefix='/admin')

    path = 'modules/user'
    dir_list = os.listdir(path)

    for fname in dir_list:
        if os.path.isdir(os.path.join(path, fname)) and os.path.exists(os.path.join(path, fname, '__init__.py')):
            f, filename, descr = imp.find_module(fname, [path])
            mods[fname] = imp.load_module(fname, f, filename, descr)
            app.register_blueprint(getattr(mods[fname], 'module'), url_prefix='/store')
        elif os.path.isfile(os.path.join(path, fname)):
            name, ext = os.path.splitext(fname)
            if ext == '.py' and not name == '__init__':
                f, filename, descr = imp.find_module(name, [path])
                mods[fname] = imp.load_module(name, f, filename, descr)
                app.register_blueprint(getattr(mods[fname], 'module'), url_prefix='/store')

load_blueprints()
print(app.url_map)

@app.route('/')
def main():
    return 'yay it works!!'

@app.route('/startSession')
def startSession():
    #stripe.api_key = stripe_keys["secret_key"]

    try:
        # Create new Checkout Session for the order
        # Other optional params include:
        # [billing_address_collection] - to display billing address details on the page
        # [customer] - if you have an existing Stripe Customer ID
        # [payment_intent_data] - lets capture the payment later
        # [customer_email] - lets you prefill the email input in the form
        # For full details see https:#stripe.com/docs/api/checkout/sessions/create

        # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
        ssession = stripe.checkout.Session.create(
            success_url=domain_url + "success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=domain_url + "cancelled",
            #payment_method_types=["card"],
            mode="payment",
            line_items=[
                {
                    "name": "Test Payment",
                    "quantity": 1,
                    "currency": "usd",
                    "amount": "2000",
                }
            ]
        )
        return redirect(ssession.url, code=303)
    except Exception as e:
        return jsonify(error=str(e)), 403

@app.route("/success")
def success():
    a = stripe.checkout.Session.retrieve(request.args['session_id'])
    return 'Thanks for your payment!<br>{}'.format(a)

@app.route("/cancelled")
def cancelled():
    return ':('

@app.route('/admin')
def admin():
    return 'admin'

app.run(host='0.0.0.0', port=80, debug=True)
