from flask import Blueprint, render_template, abort
from flask import *
from jinja2 import TemplateNotFound
import stripe
import config
import os
from werkzeug.utils import secure_filename
from core.utils.auth import auth

stripe.api_version = '2020-08-27'

module = Blueprint('Stripe', __name__)
module.hasAdminPage = True
module.moduleDescription = 'The Core Stripe Billing Module for LoonaBilling (Unofficial)'
module.version = '1.4'

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
    if os.path.isfile('configs/stripe/privateKey.txt'):
        try:
            with open('configs/stripe/privateKey.txt', 'r') as of:
                stripe.api_key = of.read().strip()
        except Exception as e:
            print('Unable to read stripe key:', e)

    cf('configs/stripe')
    cf('products')

checks()

def createProduct(data, image, description, price):
    print(data)
    print(image)
    if image == None:
        images = []
    else:
        images=[config.domain_url + image]
    if description == '':
        description = 'No description'
    prod = stripe.Product.create(name=data['title'], description=description, images=images)
    print(prod)
    prc = stripe.Price.create(
      unit_amount=price,
      currency=data['currency'],
      product=prod['id'],
    )
    return {'product': prod['id'], 'price': prc['id']}
    #prod = stripe.Product.create(name="")

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
        #print(request.args)
        ritem = secure_filename(request.args['item'])
        rcate = secure_filename(request.args['category'])
        if 'category' not in request.args:
            return render_template('error.html', msg='No category was specified.', businessName=config.businessName)
        if 'item' not in request.args:
            return render_template('error.html', msg='No item ID was specified.', businessName=config.businessName)
        if os.path.isdir('products/{}'.format(rcate)):#, request.args['item'])):
            with open('products/{}/{}.json'.format(rcate, ritem)) as of:
                data = json.load(of)
                for p in data['Config']:

                    ssession = stripe.checkout.Session.create(
                        success_url=config.domain_url + "success?session_id={CHECKOUT_SESSION_ID}",
                        cancel_url=config.domain_url + "cancelled",
                        #payment_method_types=["card"],
                        mode="payment",
                        line_items=[
                            {
                            "price": p['args']['price'],
                            "quantity": 1
                            }
                        ],
                        metadata = {'category': request.args['category'], 'itemID': request.args['item'], 'item': p['title']},
                    )
                    return redirect(ssession.url, code=303)
    except Exception as e:
        return jsonify(error=str(e)), 403

@module.route("/success")
def success():
    a = stripe.checkout.Session.retrieve(request.args['session_id'])
    # Send email after purchase. Check checkout session a['email']
    return render_template('core/Stripe/paymentSucess.html', businessName=config.businessName)

@module.route("/cancelled")
def cancelled():
    return render_template('core/Stripe/paymentCancelled.html', businessName=config.businessName)
import sys
@module.route('/admin/{}/listPurcahses'.format(module.name), methods=['GET', 'POST'])
@auth.login_required
def adminListPurchases():
    if request.method == 'POST':
        print(request.form)
        try:
            for a in request.form:
                print(a)
                b = a.split('-')
                print(b)
                if b[0].strip() == 'refund':
                    stripe.Refund.create(charge=b[1])
                if b[0].strip() == 'unrefund':
                    print('unrefund')
                    #print(stripe.Charge.retrieve(b[1])['refunds']['data'][0]['id'])
                    c = stripe.Refund.cancel(stripe.Charge.retrieve(b[1])['refunds']['data'][0]['id'])
                    return str(c)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            #return str(e)
            return redirect(url_for('Stripe.adminListPurchases'))
    try:
        bal = stripe.Balance.retrieve()["available"][0]["amount"]
    except:
        bal = '0.0'
    try:
        purchases = stripe.Charge.list() #stripe.checkout.Session.list()
    except:
        purchases = []
    try:
        refunds = stripe.Refund.list()
    except:
        refunds = []
    try:
        customers = stripe.Customer.list()
    except:
        customers = []
    #print(stripe.Balance.retrieve())
    try:
        #print(stripe.Charge.list())
        return render_template('core/Stripe/adminListPurchases.html', customers=customers, customer=stripe.Customer.retrieve, purchases=purchases, refunds=refunds, bal=bal, businessName=config.businessName, moduleName=module.name, moduleDescription=module.moduleDescription)
    except Exception as e:
        print(e)
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

@module.route('/admin/{}/emailSettings'.format(module.name))
@auth.login_required
def adminEmailSettings():
    return render_template('core/Stripe/adminEmailSettings.html', businessName=config.businessName, moduleName=module.name, moduleDescription=module.moduleDescription)


@module.route('/admin/{}/manageKeys'.format(module.name), methods=['GET', 'POST'])
@auth.login_required
def adminManageKeys():
    if 'publishableKey' in request.form:
        open('configs/stripe/publishableKey.txt', 'w+').write(request.form['publishableKey'].strip())
    if 'privateKey' in request.form:
        open('configs/stripe/privateKey.txt', 'w+').write(request.form['privateKey'].strip())
        stripe.api_key = request.form['privateKey'].strip()
    return render_template('core/Stripe/adminManageKeys.html', businessName=config.businessName, moduleName=module.name, moduleDescription=module.moduleDescription)
