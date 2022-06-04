import sys, os
import json
from flask import Flask
from flask import *
import stripe
import config
stripe.api_version = '2020-08-27'
stripe.api_key = ''
app = Flask(__name__)

@app.route('/')
def main():
    return 'yay it works!!'

@app.route('/startSession')
def startSession():
    domain_url = "http://localhost/"
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
