from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
from flask import *
from flask_hcaptcha import hCaptcha
from werkzeug.utils import secure_filename
from colorama import Fore, Back, Style
import pathlib
import requests
import config
import sys, os
from base64 import b64encode
from io import BytesIO
import imp

from core.utils.auth import hauth
from core.utils import auth
from core.utils import files

from requests_oauthlib import OAuth2Session

# OTP Libraries
import pyotp
import qrcode

module = Blueprint('MicrosoftLogin', __name__)
module.hasAdminPage = False
module.moduleDescription = 'Microsoft Login'
module.version = '1.0'
module.config = {}

# Accounts Settings
module.AccountsPage = False
module.basicName = 'microsoft'
module.fontawesome = 'fa-brands fa-microsoft'

# Microsoft Login
module.config['MICROSOFT_CLIENT_ID'] = ''
module.config['MICROSOFT_CLIENT_SECRET'] = ''
module.config['MICROSOFT_API_BASE_URL'] = 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize'
module.config['MICROSOFT_TOKEN_URL'] = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
module.config['MICROSOFT_REQUESTED_SCOPES'] = ['User.ReadBasic.All', 'openid', 'User.Read', 'email', 'profile']

def cf(folder):
	try:
		os.mkdir(folder)
		print(f'[{module.name}] Created Folder: {folder}')
	except Exception as e:
		#print(e)
		return

def checks():
    cf('data')
    cf('data/user')
    cf('data/states')
    cf('data/2fa')
    cf('configs/accounts')
    if not os.path.isfile('configs/accounts/microsoft.json'):
        data = {}
        data['Config'] = []
        data['Config'].append({
        'enabled': False,
        'client_id': '',
		'client_secret': ''
        })
        with open('configs/accounts/microsoft.json', 'w+') as of:
            json.dump(data, of)
    try:
        module.config['MICROSOFT_CLIENT_ID'] = files.readJSONVar('configs/accounts/microsoft.json', 'client_id')
        module.config['MICROSOFT_CLIENT_SECRET'] = files.readJSONVar('configs/accounts/microsoft.json', 'client_secret')
    except Exception as e:
        print(f'[{module.name}] Unable to load Microsoft Settings')

checks()

def oauth2_token_updater(token):
    session['oauth2_token'] = token

def oauth2_session(token=None, state=None, scope=None):
    return OAuth2Session(
        client_id=module.config['MICROSOFT_CLIENT_ID'],
        token=token,
        state=state,
        scope=module.config['MICROSOFT_REQUESTED_SCOPES'],
        redirect_uri=url_for('MicrosoftLogin.authorize', _external=True),
        auto_refresh_kwargs = {
            'client_id': module.config['MICROSOFT_CLIENT_ID'],
            'client_secret': module.config['MICROSOFT_CLIENT_SECRET'],
        },
        auto_refresh_url=module.config['MICROSOFT_TOKEN_URL'],
        token_updater=oauth2_token_updater)

@module.route('/callback/microsoft')
def authorize():
    if request.values.get('error'):
        error = request.values['error']
        print(error)
        return redirect(url_for('Accounts.login'))

    microsoft = oauth2_session(state=session['oauth2_state'])
    token = microsoft.fetch_token(
    module.config['MICROSOFT_TOKEN_URL'],
    client_secret=module.config['MICROSOFT_CLIENT_SECRET'],
    authorization_response=request.url,
    code=request.args['code'])

    session['oauth2_token'] = token
    r = microsoft.get('https://graph.microsoft.com/v1.0/me').json()
    #print(r)
    #r = microsoft.get('https://graph.microsoft.com/v1.0/email').json()
    #print(r)
    if '@' in r['userPrincipalName']:
        uemail = r['userPrincipalName']
    else:
        return 'Unable to login with this Microsoft Account'
    try:
        with open(f'data/states/{session["state"]}', 'r') as of:
            st = of.read().strip()
            #print(st == 'register')
            #print(st == 'login')
            of.close()
            os.remove(f'data/states/{session["state"]}')

            if st == 'register':
                if auth.isEmail(uemail):
                    return render_template('core/Accounts/register.html', msg="Account already exists with this email", businessName=files.getBranding()[0])
                userID = auth.getUserCount()
                cf(f'data/user/{userID}')
                cf(f'data/user/{userID}/payments')
                cf(f'data/user/{userID}/sessions')
                cf(f'data/user/{userID}/paydata')
                data = {}
                data['Config'] = []
                data['Config'].append({
                'email': uemail,
                'password': str(auth.encKey(uemail).decode()),
                'external': True,
                'ID': userID,
                'secret': str(pyotp.random_base32()),
                '2fa': False,
                'suspended': {'isSuspended': False, 'reason': 'No reason'},
                'type': 'user',
                'args': {'type': 'facebook'}
                })
                with open('data/user/{}/config.json'.format(userID), 'w+') as of:
                    json.dump(data, of)
                session['user'] = json.dumps(data)
                return redirect(url_for('Accounts.dashboard'))
            if st == 'login':
                #print('login')
                if auth.isEmail(uemail):
                    #return render_template('core/Accounts/register.html', msg="Account already exists with this email", businessName=files.getBranding()[0])
                    data = {}
                    data['Config'] = []
                    data['Config'].append({
                    'email': uemail,
                    'password': str(auth.encKey(uemail).decode()),
                    'external': True,
                    'ID': auth.getID(uemail)
                    })
                    userlog = auth.logAuth(data)
                    #print(user)
                    if userlog != False:
                        session['user'] = json.dumps(userlog)
                        return redirect(url_for('Accounts.dashboard'))
                    else:
                        return redirect(url_for('Accounts.login'))
                else:
                    return redirect(url_for('Accounts.register'))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(e, exc_type, fname, exc_tb.tb_lineno)

    return 'Error'
