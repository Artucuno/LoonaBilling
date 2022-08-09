import stripe
from flask import Flask
from flask import *
from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
import config
import sys, os
from colorama import Fore, Back, Style
from colorama import init
import imp
from core.utils import files as fls
from werkzeug.utils import secure_filename
from core.utils.auth import hauth, login_is_required
from core.utils import files
from core.utils import auth
from core.utils import stripeutils
from core.utils import autoutils
from datetime import datetime

# https://stripe.com/docs/billing/subscriptions/webhooks


module = Blueprint('Stripe', __name__)
module.hasAdminPage = False
module.moduleDescription = 'Stripe Module'
module.version = '2.0'
module.supportedMethods = ['payment', 'subscription']

stripe.api_key = 'sk_test_51HMpbpEVF5vnLBwDxNNzXC2QQwAiGcJ60fnGC6MIeR9VWcrC2Uzr5sTmUzHGPqNMfnYDD35IXsXWCO9pZRKkbiBI00Gk3nfJar'

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

def getItem(category, item):
    category = secure_filename(item)
    item = secure_filename(item)
    with open(f'products/{category}/{item}.json') as of:
        data = json.load(of)
        return data['Config'][0]

def parsePrice(price):
    prc = list(price)
    prc.insert(-2, '.')
    return ''.join(prc)

def getCart(token):
    token = secure_filename(token)
    if os.path.isfile(f'data/cart/{token}'):
        with open(f'data/cart/{token}') as of:
            data = json.load(of)
            return data['Config'][0]['cart']
    else:
        return False

def parseItems(args):
    if args['type'] == 'buy':
        i = getItem(args['category'], args['item'])
        print(i)
        desc = 'No description'
        img = None
        if i['description'].strip() != '':
            desc = i['description']
        if i['image'] != None:
            img = config.domain_url + i['image']
        mode = 'payment'
        modes = ['payment', 'subscription']
        try:
            md = request.args['mode']
            if md not in modes:
                mode = 'payment'
            else:
                mode = md
        except:
            mode = 'payment'
        if mode == 'payment':
            return [{
            'amount': i['price'],
            'currency': i['currency'],
            'quantity': 1,
            'name': i['title'],
            'description': desc,
            'images': [img],
            }], {'items': [i['title'], args['category'], args['item']]}
        elif mode == 'subscription':
            return [{
            'quantity': 1,
            'price_data': {
                'recurring': {"interval": "month"},
                'unit_amount': i['price'],
                'currency': i['currency'],
                'product_data': {
                    'name': i['title'],
                    'description': desc,
                    'images': [img],
                },
            },
            }], {'items': [i['title'], args['category'], args['item']]}
            # pain
        else:
            return False, {}
        # https://upload.wikimedia.org/wikipedia/en/9/95/Test_image.jpg,
    elif args['type'] == 'cart':
        cart = getCart(args['cartid'])
        if cart != False:
            a = []
            print(cart)
            mtd = []
            for f in cart:
                print(f)
                i = getItem(f['category'], f['item'])
                print(i)
                desc = 'No description'
                img = None
                if i['description'].strip() != '':
                    desc = i['description']
                if i['image'] != None:
                    img = config.domain_url + i['image']
                a += [{
                'amount': i['price'],
                'currency': i['currency'],
                'quantity': 1,
                'name': i['title'],
                'description': desc,
                'images': [img],
                #'metadata': {'test': 'test'}
                }]
                mtd += [i['title'], f['category'], f['item']]
            return a, {'items': mtd}
        else:
            return False, {}

@module.route('/Stripe/payment')
@login_is_required
def payment():
    # Create new Checkout Session for the order
    # Other optional params include:
    # [billing_address_collection] - to display billing address details on the page
    # [customer] - if you have an existing Stripe Customer ID
    # [payment_intent_data] - lets capture the payment later
    # [customer_email] - lets you prefill the email input in the form
    # For full details see https:#stripe.com/docs/api/checkout/sessions/create

    # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
    #print(request.args)
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
            modes = ['payment', 'subscription']
            try:
                md = request.args['mode']
                if md not in modes:
                    return 'Invalid mode'
                mode = md
            except:
                mode = 'payment'
            items, mtd = parseItems(request.args)
            print(items)
            if items == False:
                return 'No items, try restarting your session'
            #print(user)
            print('user' in p['args'])
            if 'user' not in p['args']:
                cust_setup = stripe.Customer.create(email=p['email'])
                cust = cust_setup.id
                files.updateJSONargs('data/user/{}/config.json'.format(p['ID']), 'StripeCustomer', cust)
            else:
                cust = p['args']['StripeCustomer']

            ssession = stripe.checkout.Session.create(
                success_url=config.domain_url + "success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=config.domain_url + "cancelled?session_id={CHECKOUT_SESSION_ID}",
                payment_method_types=["card"],
                mode=mode,
                #customer_email=p['email'],
                line_items=items,
                customer=cust,
                client_reference_id=cartid,
                metadata={'items': str(json.dumps(mtd)), 'cartid': cartid}
            )
            #print(ssession)
            pid = len(os.listdir('data/user/{}/sessions'.format(p['ID'])))
            dt = {}
            dt['Config'] = []
            dt['Config'].append({
            'provider': module.name,
            'session': json.loads(str(ssession)),
            'time': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'pid': pid,
            'mode': mode,
            'payment_intent': ssession.payment_intent,
            'cartid': cartid,
            'mtd': mtd
            })
            with open('data/user/{}/sessions/{}'.format(p['ID'], ssession.payment_intent), 'w+') as of:
                json.dump(dt, of)
            return redirect(ssession.url, code=303)

@module.route('/calltest', methods=['GET', 'POST'])
def calltest():
    print(request.headers)
    print(request.form)
    print(request.data)
    return 'YAY'

endpoint_secret = 'whsec_5bd944db308fd8c36176b422a8e8f369abf4fe2acb4967c627c5ddcfc6f12e81'
@module.route(f'/{module.name}/webhook', methods=['POST'])
def webhook():
    event = None
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e

    # subscription
    # - Save invoice data
    # - subscription created
    #   - Get invoice (Payment intent in invoice)
    # - Automation
    #   - tuple(list)

    # Payments
    # - charge.succeeded
    # - payment_intent.succeeded

    # Subscription
    # -
    try:
        if event['type'].startswith('invoice.'):
            print(event['type'], event['data']['object']['customer_email'])
            uid = auth.getID(event['data']['object']['customer_email'])
            cf(f'data/user/{uid}/payments')
            cf('data/user/{}/payments/{}'.format(uid, event['data']['object']['payment_intent']))
            cf('data/user/{}/payments/{}/products'.format(uid, event['data']['object']['payment_intent']))
            cf('data/user/{}/payments/{}/logs'.format(uid, event['data']['object']['payment_intent']))
            cf('data/user/{}/payments/{}/paydata'.format(uid, event['data']['object']['payment_intent']))
            with open('data/user/{}/payments/{}/paydata/{}.json'.format(uid, event['data']['object']['payment_intent'], event['type']), 'w+') as of:
                json.dump(json.loads(str(event)), of)
        if event['type'] == 'invoice.paid':
            print('paid', event)
        if event['type'] == 'payment_intent.created':
            #print(event)
            with open('data/user/{}/{}.json'.format(auth.getID(event['data']['object']['receipt_email']), event['type']), 'w+') as of:
                json.dump(event, of)
            print(event['data']['object']['receipt_email'])
            print(event['data']['object']['id'])
            uid = auth.getID(event['data']['object']['receipt_email'])
            cf(f'data/user/{uid}/payments')
            cf('data/user/{}/payments/{}'.format(uid, event['data']['object']['id']))
            cf('data/user/{}/payments/{}/products'.format(uid, event['data']['object']['id']))
            cf('data/user/{}/payments/{}/logs'.format(uid, event['data']['object']['id']))
            cf('data/user/{}/payments/{}/paydata'.format(uid, event['data']['object']['id']))
            with open('data/user/{}/payments/{}/config.json'.format(uid, event['data']['object']['id']), 'w+') as of:
                json.dump(json.loads(str(event)), of)
            dt = {}
            dt['Config'] = []
            dt['Config'].append({
            'status': event['data']['object']['status'],
            'time': int(datetime.timestamp(datetime.now()))
            })
            with open('data/user/{}/payments/{}/status.json'.format(uid, event['data']['object']['id']), 'w+') as of:
                json.dump(dt, of)

        if event['type'] == 'payment_intent.succeeded':
            #print(event)
            #uid = auth.getID(event['data']['object']['receipt_email'])
            #with open('configs/stri/{}.json'.format(event['type']), 'w+') as of:
            #    json.dump(event, of)
            print(event)
            with open('data/user/{}/{}.json'.format(auth.getID(event['data']['object']['receipt_email']), event['type']), 'w+') as of:
                json.dump(event, of)
            print(event['data']['object']['receipt_email'])
            print(event['data']['object']['id'])
            uid = auth.getID(event['data']['object']['receipt_email'])
            cf(f'data/user/{uid}/payments')
            cf('data/user/{}/payments/{}'.format(uid, event['data']['object']['id']))
            cf('data/user/{}/payments/{}/products'.format(uid, event['data']['object']['id']))
            cf('data/user/{}/payments/{}/logs'.format(uid, event['data']['object']['id']))
            cf('data/user/{}/payments/{}/paydata'.format(uid, event['data']['object']['id']))
            with open('data/user/{}/payments/{}/config.json'.format(uid, event['data']['object']['id']), 'w+') as of:
                json.dump(json.loads(str(event)), of)
            dt = {}
            dt['Config'] = []
            dt['Config'].append({
            'status': event['data']['object']['status'],
            'time': int(datetime.timestamp(datetime.now()))
            })
            with open('data/user/{}/payments/{}/status.json'.format(uid, event['data']['object']['id']), 'w+') as of:
                json.dump(dt, of)

        if event['type'] == 'charge.succeeded':
            #print(event)
            cuser = stripeutils.getPaymentCustomer(event['data']['object']['payment_intent'])
            with open('data/user/{}/sessions/{}'.format(cuser, event['data']['object']['payment_intent'])) as of:
                data = json.load(of)
                print(data)
                for p in data['Config']:
                    if os.path.isfile('data/cart/{}'.format(p['cartid'])):
                        with open('data/cart/{}'.format(p['cartid'])) as of:
                            data = json.load(of)
                            for p in data['Config']:
                                for pp in p['cart']:
                                    a = getItem(pp['category'], pp['item'])
                                    auto = tuple(a['automation'])
                                    print(autoutils.runAutomation(auto[0].split('-')[0], auto[0].split('-')[1], auto[1:][0].split(', ')))

        #payment_intent
        if event['type'] == 'checkout.session.completed':
            #print(event)
            #with open('configs/stri/{}.json'.format(event['type']), 'w+') as of:
            #    json.dump(event, of)
            uid = auth.getID(event['data']['object']['customer_details']['email'])
            dt = {}
            dt['Config'] = []
            dt['Config'].append({
            'status': event['data']['object']['payment_status'],
            'time': int(datetime.timestamp(datetime.now()))
            })
            with open('data/user/{}/payments/{}/status.json'.format(uid, event['data']['object']['payment_intent']), 'w+') as of:
                json.dump(dt, of)
            with open('data/user/{}/payments/{}/paydata/checkout.json'.format(uid, event['data']['object']['payment_intent']), 'w+') as of:
                json.dump(json.loads(str(event)), of)
            #payment_status
            #print(event['data']['object']['id'])
            #try:
            #    print(stripe.Charge.retrieve(event['data']['object']['id']))
            #except Exception as e:
            #    print(e)

        # Handle the event
        print('Unhandled event type {}'.format(event['type']))
        return jsonify(success=True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(event['type'], e, exc_type, fname, exc_tb.tb_lineno)
        return jsonify(success=False)

@module.route('/admin/{}'.format(module.name))
@hauth.login_required
def adminPage():
    try:
        bal = stripe.Balance.retrieve()["available"][0]["amount"]
    except:
        bal = '0.0'
    #print(stripe.Balance.retrieve())
    return render_template('core/Stripe/admin.html', bal=bal, businessName=files.getBranding()[0], moduleName=module.name, moduleDescription=module.moduleDescription)

@module.route('/admin/{}/emailSettings'.format(module.name))
@hauth.login_required
def adminEmailSettings():
    return render_template('core/Stripe/adminEmailSettings.html', businessName=files.getBranding()[0], moduleName=module.name, moduleDescription=module.moduleDescription)

@module.route('/admin/{}/manageKeys'.format(module.name), methods=['GET', 'POST'])
@hauth.login_required
def adminManageKeys():
    if 'publishableKey' in request.form:
        open('configs/stripe/publishableKey.txt', 'w+').write(request.form['publishableKey'].strip())
    if 'privateKey' in request.form:
        open('configs/stripe/privateKey.txt', 'w+').write(request.form['privateKey'].strip())
        stripe.api_key = request.form['privateKey'].strip()
    return render_template('core/Stripe/adminManageKeys.html', businessName=files.getBranding()[0], moduleName=module.name, moduleDescription=module.moduleDescription)
