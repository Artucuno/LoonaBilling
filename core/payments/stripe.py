from flask import Blueprint, render_template, abort
from flask import *
from jinja2 import TemplateNotFound
import stripe
import config
import os
from core.utils.auth import auth
module = Blueprint('Stripe', __name__)
module.hasAdminPage = True
module.moduleDescription = 'The Core Stripe Billing Module for LoonaBilling (Unofficial)'
module.version = '1.3'

# TODO
# https://stripe.com/docs/api/charges/list?lang=python
# https://stripe.com/docs/api/refunds/create?lang=python

def cf(folder):
    try:
        os.mkdir(folder)
        print(f'[{module.name}] Created Folder: {folder}')
    except Exception as e:
        #print(e)
        return

def checks():
    try:
        stripe.api_version = '2020-08-27'

        if os.path.isfile('configs/stripe/privateKey.txt'):
            with open('configs/stripe/privateKey.txt', 'r') as of:
                stripe.api_key = of.read().strip()
    except Exception as e:
        print(e)
        cf('configs/stripe')

    cf('products')

checks()

@module.route(f'/{module.name}/startSession')
def Stripe_startSession():
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
            return render_template('error.html', msg='No category was specified.', businessName=config.businessName)
        if 'item' not in request.args:
            return render_template('error.html', msg='No item ID was specified.', businessName=config.businessName)
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
                                "currency": str(p['currency']).lower(),
                                "amount": int(p['price'].replace('.', '')),
                                "description": str(p['description']),
                                #"metadata": {'category': request.args['category'], 'itemID': request.args['item'], 'item': p['title']},
                            }
                        ],
                        #description=p['description'],
                        metadata = {'category': request.args['category'], 'itemID': request.args['item'], 'item': p['title']},
                    )
                    return redirect(ssession.url, code=303)
    except Exception as e:
        return jsonify(error=str(e)), 403

@module.route("/success")
def success():
    a = stripe.checkout.Session.retrieve(request.args['session_id'])
    return render_template('core/Stripe/paymentSucess.html', businessName=config.businessName)

@module.route("/cancelled")
def cancelled():
    return render_template('core/Stripe/paymentCancelled.html', businessName=config.businessName)

@module.route('/admin/{}/listPurcahses'.format(module.name))
@auth.login_required
def adminListPurchases():
    try:
        bal = stripe.Balance.retrieve()["available"][0]["amount"]
    except:
        bal = '0.0'
    try:
        purchases = stripe.Charge.list()
    except:
        purchases = 'Unable to get'
    #print(stripe.Balance.retrieve())
    try:
        return render_template('core/Stripe/adminListPurchases.html', purchases=purchases, bal=bal, businessName=config.businessName, moduleName=module.name, moduleDescription=module.moduleDescription)
    except:
        return 'Unable to get. Have you added an API Key?'

@module.route('/admin/{}'.format(module.name))
@auth.login_required
def adminPage():
    try:
        bal = stripe.Balance.retrieve()["available"][0]["amount"]
    except:
        bal = '0.0'
    #print(stripe.Balance.retrieve())
    return render_template('core/Stripe/admin.html', bal=bal, businessName=config.businessName, moduleName=module.name, moduleDescription=module.moduleDescription)

@module.route('/admin/{}/manageKeys'.format(module.name), methods=['GET', 'POST'])
@auth.login_required
def adminManageKeys():
    if 'publishableKey' in request.form:
        open('configs/stripe/publishableKey.txt', 'w+').write(request.form['publishableKey'].strip())
    if 'privateKey' in request.form:
        open('configs/stripe/privateKey.txt', 'w+').write(request.form['privateKey'].strip())
        stripe.api_key = request.form['privateKey'].strip()
    return render_template('core/Stripe/adminManageKeys.html', businessName=config.businessName, moduleName=module.name, moduleDescription=module.moduleDescription)
