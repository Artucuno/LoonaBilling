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

from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

from core.utils.auth import hauth
from core.utils import auth
from core.utils import files

from requests_oauthlib import OAuth2Session

# OTP Libraries
import pyotp
import qrcode

module = Blueprint('GoogleLogin', __name__)
module.hasAdminPage = False
module.moduleDescription = 'Google Login'
module.version = '1.0'
module.config = {}

# Accounts Settings
module.AccountsPage = False
module.basicName = 'google'
module.fontawesome = 'fa-brands fa-google'

# Google Login
module.config['GOOGLE_API_BASE_URL'] = ''

def oauth2_session(cid):
    return module.flow

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
    if not os.path.isfile('configs/accounts/google.json'):
        data = {}
        data['Config'] = []
        data['Config'].append({
        'enabled': False,
        'client_id': '',
        'file': 'configs/accounts/client_secret.json'
        })
        with open('configs/accounts/google.json', 'w+') as of:
            json.dump(data, of)
    try:
        with open('configs/accounts/google.json') as of:
            dt = json.load(of)
            for p in dt['Config']:
                try:
                    module.config['GOOGLE_CLIENT_ID'] = p['client_id']
                except Exception as e:
                    print(e)
                    module.config['GOOGLE_CLIENT_ID'] = ''
                try:
                    module.flow = Flow.from_client_secrets_file(
                    client_secrets_file='configs/accounts/client_secret.json',
                    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
                    redirect_uri=config.domain_url+"callback/google"
                    )
                except Exception as e:
                    print(Fore.YELLOW + f'[{module.name}] ' + Style.RESET_ALL + 'Unable to load Google Flow', e)#, e)
    except Exception as e:
        print('Accounts checks', e)

checks()

@module.route("/callback/google") # Google Callback
def authorize():
	module.flow.fetch_token(authorization_response=request.url)
	#print(session['state'])

	if not session["state"] == request.args["state"]:
		abort(500)  #state does not match!

	credentials = module.flow.credentials
	request_session = requests.session()
	cached_session = cachecontrol.CacheControl(request_session)
	token_request = google.auth.transport.requests.Request(session=cached_session)

	id_info = id_token.verify_oauth2_token(
		id_token=credentials._id_token,
		request=token_request,
		audience=module.config['GOOGLE_CLIENT_ID']
	)
	#print(id_info)
	try:
		with open(f'data/states/{session["state"]}', 'r') as of:
			st = of.read().strip()
			#print(st == 'register')
			#print(st == 'login')
			of.close()
			os.remove(f'data/states/{session["state"]}')

			if st == 'register':
				if auth.isEmail(id_info['email']):
					return render_template('core/Accounts/register.html', msg="Account already exists with this email", businessName=files.getBranding()[0])
				userID = auth.getUserCount()
				cf(f'data/user/{userID}')
				cf(f'data/user/{userID}/payments')
				cf(f'data/user/{userID}/sessions')
				cf(f'data/user/{userID}/paydata')
				data = {}
				data['Config'] = []
				data['Config'].append({
				'email': id_info['email'],
				'password': str(auth.encKey(id_info['email']).decode()),
				'external': True,
				'ID': userID,
				'secret': str(pyotp.random_base32()),
				'2fa': False,
				'suspended': {'isSuspended': False, 'reason': 'No reason'},
				'type': 'user',
				'args': {'type': 'google'}
				})
				with open('data/user/{}/config.json'.format(userID), 'w+') as of:
					json.dump(data, of)
				session['user'] = json.dumps(data)
				return redirect(url_for('Accounts.dashboard'))
			if st == 'login':
				#print('login')
				if auth.isEmail(id_info['email']):
					#return render_template('core/Accounts/register.html', msg="Account already exists with this email", businessName=files.getBranding()[0])
					data = {}
					data['Config'] = []
					data['Config'].append({
					'email': id_info['email'],
					'password': str(auth.encKey(id_info['email']).decode()),
					'external': True,
					'ID': auth.getID(id_info['email'])
					})
					user = auth.logAuth(data)
					#print(user)
					if user != False:
						session['user'] = json.dumps(user)
						return redirect(url_for('Accounts.dashboard'))
					else:
						return redirect(url_for('Accounts.login'))
				else:
					return redirect(url_for('Accounts.register'))
	except Exception as e:
		print(e)
	return 'Error'
