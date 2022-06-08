from flask import Blueprint, render_template, abort
from flask import *
from jinja2 import TemplateNotFound
import stripe
import config
import os
module = Blueprint('Stripe', __name__)
module.hasAdminPage = True
module.moduleDescription = 'The Core Stripe Billing Module for LoonaBilling (Unofficial)'
module.version = '1.1'

def cf(folder):
    try:
        os.mkdir(folder)
        print(f'[{module.name}] Created Folder: {folder}')
    except Exception as e:
        #print(e)
        pass

def checks():
    try:
        import configs.stripe.config as stripeConfig
        stripe.api_version = stripeConfig.api_version
        stripe.api_key = stripeConfig.api_key
    except Exception as e:
        print(e)
        cf('configs/stripe')
        a = open('configs/stripe/config.py', 'w+').write('''# This is not an official module made by Stripe.
api_version = ''
api_key = ''
''')
        try:
            import configs.stripe.config as stripeConfig
            print("Stripe config was created. Please update the config located at configs/stripe/config.py")
        except:
            print('ERROR: STRIPE CONFIG NOT FOUND')

    cf('products')

checks()

@module.route('/startSession')
def startSession():
    try:
        # Create new Checkout Session for the order
        # Other optional params include:
        # [billing_address_collection] - to display billing address details on the page
        # [customer] - if you have an existing Stripe Customer ID
        # [payment_intent_data] - lets capture the payment later
        # [customer_email] - lets you prefill the email input in the form
        # For full details see https:#stripe.com/docs/api/checkout/sessions/create

        # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
        print(request.args)
        if 'category' not in request.args:
            return 'Needs category'
        if 'item' not in request.args:
            return 'Needs item'
        if os.path.isdir('products/{}'.format(request.args['category'])):#, request.args['item'])):
            with open('products/{}/{}.json'.format(request.args['category'], request.args['item'])) as of:
                data = json.load(of)
                for p in data['Config']:

                    ssession = stripe.checkout.Session.create(
                        success_url=config.domain_url + "success?session_id={CHECKOUT_SESSION_ID}",
                        cancel_url=config.domain_url + "cancelled",
                        #payment_method_types=["card"],
                        mode="payment",
                        line_items=[
                            {
                                "name": str(p['title']),
                                "quantity": 1,
                                "currency": "usd",
                                "amount": int(p['price'].replace('.', '')),
                            }
                        ],
                        #metadata={request.args}
                    )
                    return redirect(ssession.url, code=303)
    except Exception as e:
        return jsonify(error=str(e)), 403

@module.route("/success")
def success():
    a = stripe.checkout.Session.retrieve(request.args['session_id'])
    return 'Thanks for your payment!<br>{}'.format(a)

@module.route("/cancelled")
def cancelled():
    return ':('

@module.route('/admin/{}'.format(module.name))
def adminPage():
    return render_template('core/Stripe/admin.html', businessName=config.businessName, moduleName=module.name, moduleDescription=module.moduleDescription)

@module.route('/admin/{}/manageKeys'.format(module.name), methods=['GET', 'POST'])
def adminManageKeys():
    if 'publishableKey' in request.form:
        open('configs/stripe/publishableKey.txt', 'w+').write(request.form['publishableKey'].strip())
    if 'privateKey' in request.form:
        open('configs/stripe/privateKey.txt', 'w+').write(request.form['privateKey'].strip())
        stripe.api_key = request.form['privateKey'].strip()
    return render_template('core/Stripe/adminManageKeys.html', businessName=config.businessName, moduleName=module.name, moduleDescription=module.moduleDescription)
