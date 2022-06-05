from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
import stripe
import config
import os
module = Blueprint('Stripe', __name__)

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
        ssession = stripe.checkout.Session.create(
            success_url=config.domain_url + "success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=config.domain_url + "cancelled",
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

@module.route("/success")
def success():
    a = stripe.checkout.Session.retrieve(request.args['session_id'])
    return 'Thanks for your payment!<br>{}'.format(a)

@module.route("/cancelled")
def cancelled():
    return ':('
