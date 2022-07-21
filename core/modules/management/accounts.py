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

from core.utils.auth import hauth
from core.utils import auth
from core.utils import files

from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

from requests_oauthlib import OAuth2Session

# OTP Libraries
import pyotp
import qrcode

module = Blueprint('Accounts', __name__)
module.hasAdminPage = True
module.moduleDescription = 'A simple accounts module'
module.version = '1.2'
module.config = {}
# hCaptcha
module.hcaptcha = hCaptcha(module)

#OAuthlib
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# Discord Login
module.config['DISCORD_API_BASE_URL'] = 'https://discordapp.com/api'
module.config['DISCORD_BASE_AUTH_URL'] = module.config['DISCORD_API_BASE_URL'] + '/oauth2/authorize'
module.config['DISCORD_TOKEN_URL'] = module.config['DISCORD_API_BASE_URL'] + '/oauth2/token'
module.config['DISCORD_REQUESTED_SCOPES'] = ['identify', 'email']

# Github Login
module.config['GITHUB_CLIENT_ID'] = ''
module.config['GITHUB_CLIENT_SECRET'] = ''
module.config['GITHUB_API_BASE_URL'] = 'https://github.com/login/oauth/authorize'
module.config['GITHUB_TOKEN_URL'] = 'https://github.com/login/oauth/access_token'
module.config['GITHUB_REQUESTED_SCOPES'] = ['user']

def oauth2_token_updater(token):
	session['oauth2_token'] = token

def oauth2_session(token=None, state=None, scope=None):
	return OAuth2Session(
		client_id=module.config['DISCORD_CLIENT_ID'],
		token=token,
		state=state,
		scope=scope,
		redirect_uri=url_for('.authorizedis', _external=True),
		auto_refresh_kwargs = {
			'client_id': module.config['DISCORD_CLIENT_ID'],
			'client_secret': module.config['DISCORD_CLIENT_SECRET'],
		},
		auto_refresh_url=module.config['DISCORD_TOKEN_URL'],
		token_updater=oauth2_token_updater)

def github_oauth2_session(token=None, state=None, scope=None):
	return OAuth2Session(
		client_id=module.config['GITHUB_CLIENT_ID'],
		token=token,
		state=state,
		scope=module.config['GITHUB_REQUESTED_SCOPES'],
		redirect_uri=url_for('.authorizegit', _external=True),
		auto_refresh_kwargs = {
			'client_id': module.config['GITHUB_CLIENT_ID'],
			'client_secret': module.config['GITHUB_CLIENT_SECRET'],
		},
		auto_refresh_url=module.config['GITHUB_TOKEN_URL'],
		token_updater=oauth2_token_updater)

def discord_get_user():
	discord = oauth2_session(token=session.get('oauth2_token'))
	user_dat = discord.get(module.config['DISCORD_API_BASE_URL'] + '/users/@me').json()
	print(user_dat)
	return user_dat

def discord_get_guilds():
	discord = oauth2_session(token=session.get('oauth2_token'))
	guilds_dat = discord.get(module.config['DISCORD_API_BASE_URL'] + '/users/@me/guilds').json()
	print(guilds_dat)
	return guilds_dat

def discord_get_connections():
	discord = oauth2_session(token=session.get('oauth2_token'))
	connections_dat = discord.get(module.config['DISCORD_API_BASE_URL'] + '/users/@me/connections').json()
	print(connections_dat)
	return connections_dat

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
	if not os.path.isfile('configs/accounts/otp.txt'):
		open('configs/accounts/otp.txt', 'w+').write(pyotp.random_base32())
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
	if not os.path.isfile('configs/accounts/discord.json'):
		data = {}
		data['Config'] = []
		data['Config'].append({
		'enabled': False,
		'client_id': '',
		'client_secret': ''
		})
		with open('configs/accounts/discord.json', 'w+') as of:
			json.dump(data, of)
	if not os.path.isfile('configs/accounts/github.json'):
		data = {}
		data['Config'] = []
		data['Config'].append({
		'enabled': False,
		'client_id': '',
		'client_secret': ''
		})
		with open('configs/accounts/github.json', 'w+') as of:
			json.dump(data, of)
	if not os.path.isfile('configs/accounts/hCaptcha.json'):
		data = {}
		data['Config'] = []
		data['Config'].append({
		'enabled': False,
		'site_key': '',
		'secret_key': ''
		})
		with open('configs/accounts/hCaptcha.json', 'w+') as of:
			json.dump(data, of)
	try:
		HCAPTCHA_ENABLED = files.readJSONVar('configs/accounts/hCaptcha.json', 'enabled')
		HCAPTCHA_SITE_KEY = files.readJSONVar('configs/accounts/hCaptcha.json', 'site_key')
		HCAPTCHA_SECRET_KEY = files.readJSONVar('configs/accounts/hCaptcha.json', 'secret_key')
		module.config['HCAPTCHA_ENABLED'] = files.readJSONVar('configs/accounts/hCaptcha.json', 'enabled')
		module.config['HCAPTCHA_SITE_KEY'] = files.readJSONVar('configs/accounts/hCaptcha.json', 'site_key')
		module.config['HCAPTCHA_SECRET_KEY'] = files.readJSONVar('configs/accounts/hCaptcha.json', 'secret_key')
		module.hcaptcha = hCaptcha(module)
	except Exception as e:
		print('[Accounts] Unable to load hCaptcha settings')
	try:
		module.config['DISCORD_CLIENT_ID'] = files.readJSONVar('configs/accounts/discord.json', 'client_id')
		module.config['DISCORD_CLIENT_SECRET'] = files.readJSONVar('configs/accounts/discord.json', 'client_secret')
	except Exception as e:
		print('[Accounts] Unable to load Discord Settings')
	try:
		with open('configs/accounts/google.json') as of:
			dt = json.load(of)
			for p in dt['Config']:
				try:
					module.GOOGLE_CLIENT_ID = p['client_id']
				except Exception as e:
					print(e)
					module.GOOGLE_CLIENT_ID = ''
				try:
					module.flow = Flow.from_client_secrets_file(
						client_secrets_file='configs/accounts/client_secret.json',
						scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
						redirect_uri=config.domain_url+"callback/google"
					)
				except Exception as e:
					print(Fore.YELLOW + f'[{module.name}] ' + Style.RESET_ALL + 'Unable to load Google Flow')#, e)
	except Exception as e:
		print('Accounts checks', e)
	try:
		for f in os.listdir('data/states'):
			try:
				os.remove(f'data/states/{f}')
			except:
				print('[Accounts] Unable to remove {f} state')
	except:
		print()

@module.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		if 'login-google' in request.form:
			authorization_url, state = module.flow.authorization_url()  #asking the flow class for the authorization (login) url
			session["state"] = state
			with open(f'data/states/{state}', 'w+') as of:
				of.write('login')
			return redirect(authorization_url)
		if 'login-discord' in request.form:
			discord = oauth2_session(scope=module.config['DISCORD_REQUESTED_SCOPES'])
			auth_url, state = discord.authorization_url(module.config['DISCORD_BASE_AUTH_URL'])
			session['oauth2_state'] = state
			session['next'] = ''
			session["state"] = state
			with open(f'data/states/{state}', 'w+') as of:
				of.write('login')
			#print(state)
			return redirect(auth_url)
		if 'login-github' in request.form:
			github = OAuth2Session(module.config['GITHUB_CLIENT_ID'], redirect_uri=url_for('.authorizegit', _external=True))
			authorization_url, state = github.authorization_url(module.config['GITHUB_API_BASE_URL'])
			session['state'] = state
			session['oauth2_state'] = state
			with open(f'data/states/{state}', 'w+') as of:
				of.write('login')
			return redirect(authorization_url)
		try:
			email = request.form['email']
			password = request.form['password']
		except:
			return render_template('core/Accounts/login.html', msg="Missing an argument", businessName=files.getBranding()[0])
		if module.config['HCAPTCHA_ENABLED']:
			if not hcaptcha.verify():
				return render_template('core/Accounts/login.html', msg="Please retry the Captcha", businessName=files.getBranding()[0])
		#if auth.isEmail(email):
		#	return render_template('core/Accounts/login.html', msg="Account already exists with this email", businessName=files.getBranding()[0])
		data = {}
		data['Config'] = []
		data['Config'].append({
		'email': email,
		'password': str(auth.encKey(password).decode()),
		'external': False,
		'ID': auth.getID(email),
		'args': {}
		})
		user = auth.logAuth(data)
		if user != False:
			if auth.getUser(auth.getID(email))['Config'][0]['2fa']:
				session['2fa'] = auth.gen2FA(data)
				return redirect(url_for('Accounts.twofa'))
			session['user'] = json.dumps(user)
			return redirect(url_for('Accounts.dashboard'))
		else:
			return render_template('core/Accounts/login.html', msg='Incorrect email or password', businessName=files.getBranding()[0])

	return render_template('core/Accounts/login.html', githubLogin=files.readJSONVar('configs/accounts/github.json', 'enabled'), googleLogin=files.readJSONVar('configs/accounts/google.json', 'enabled'), discordLogin=files.readJSONVar('configs/accounts/discord.json', 'enabled'), businessName=files.getBranding()[0])

@module.route('/2fa', methods=['GET', 'POST'])
def twofa():
	if '2fa' in session:
		with open('data/2fa/{}'.format(session['2fa'])) as of:
			data = json.load(of)
			for p in data['Config']:
				user = auth.getUser(auth.getID(p['email']))
				if request.method == 'POST':
					if pyotp.totp.TOTP(user['Config'][0]['secret']).verify(request.form['2fa']):
						session['user'] = json.dumps(data)
						session['2fa'] = None
						return redirect(url_for('Accounts.dashboard'))
					else:
						return render_template('core/Accounts/2fa.html', msg='Incorrect Code', businessName=files.getBranding()[0])
				return render_template('core/Accounts/2fa.html', businessName=files.getBranding()[0])
	return redirect(url_for('Accounts.dashboard'))

@module.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		if 'signup-google' in request.form:
			authorization_url, state = module.flow.authorization_url()  #asking the flow class for the authorization (login) url
			session["state"] = state
			with open(f'data/states/{state}', 'w+') as of:
				of.write('register')
			return redirect(authorization_url)
		if 'signup-discord' in request.form:
			discord = oauth2_session(scope=module.config['DISCORD_REQUESTED_SCOPES'])
			auth_url, state = discord.authorization_url(module.config['DISCORD_BASE_AUTH_URL'])
			session['oauth2_state'] = state
			session['next'] = ''
			session["state"] = state
			with open(f'data/states/{state}', 'w+') as of:
				of.write('register')
			#print(state)
			return redirect(auth_url)
		if 'signup-github' in request.form:
			github = OAuth2Session(module.config['GITHUB_CLIENT_ID'], redirect_uri=url_for('.authorizegit', _external=True))
			authorization_url, state = github.authorization_url(module.config['GITHUB_API_BASE_URL'])
			session['state'] = state
			session['oauth2_state'] = state
			with open(f'data/states/{state}', 'w+') as of:
				of.write('register')
			return redirect(authorization_url)
		try:
			email = request.form['email']
			password = request.form['password']
		except:
			return render_template('core/Accounts/register.html', msg="Missing an argument", businessName=files.getBranding()[0])
		if module.config['HCAPTCHA_ENABLED']:
			if not hcaptcha.verify():
				return render_template('core/Accounts/register.html', msg="Please retry the Captcha", businessName=files.getBranding()[0])
		if auth.isEmail(email):
			return render_template('core/Accounts/register.html', msg="Account already exists with this email", businessName=files.getBranding()[0])
		userID = auth.getUserCount()
		cf('data/user/{}'.format(userID))
		data = {}
		data['Config'] = []
		data['Config'].append({
		'email': email,
		'password': str(auth.encKey(password).decode()),
		'external': False,
		'ID': userID,
		'type': 'user',
		'secret': str(pyotp.random_base32()),
		'2fa': False,
		'suspended': {'isSuspended': False, 'reason': 'No reason'},
		'args': {}
		})
		with open('data/user/{}/config.json'.format(userID), 'w+') as of:
			json.dump(data, of)
		session['user'] = json.dumps(data)

		return redirect(url_for('Accounts.dashboard'))
	return render_template('core/Accounts/register.html', githubLogin=files.readJSONVar('configs/accounts/github.json', 'enabled'), googleLogin=files.readJSONVar('configs/accounts/google.json', 'enabled'), discordLogin=files.readJSONVar('configs/accounts/discord.json', 'enabled'), businessName=files.getBranding()[0])

@module.route('/suspended')
def suspended():
	return render_template('error.html', msg='Your account has been suspended.')

@module.route('/logout', methods=['GET', 'POST'])
def logout():
	try:
		session.clear()
		#session.pop('user', None)
	except Exception as e:
		print(e)
	return redirect(url_for('Accounts.login'))

@module.route('/callback/github')
def authorizegit():
	if request.values.get('error'):
		error = request.values['error']
		print(error)
		return redirect(url_for('Accounts.login'))

	github = github_oauth2_session(state=session['oauth2_state'])
	token = github.fetch_token(
	module.config['GITHUB_TOKEN_URL'],
	client_secret=module.config['GITHUB_CLIENT_SECRET'],
	authorization_response=request.url,
	code=request.args['code'])

	session['oauth2_token'] = token
	r = github.get('https://api.github.com/user')
	ems = github.get('https://api.github.com/user/emails')
	for f in json.loads(ems.content):
		if f['primary']:
			uemail = f['email']

	user = json.loads(r.content)
	#print(user['email'])
	#if user['email'] == None:
	#	return str(user)
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
				cf('data/user/{}'.format(userID))
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
				'args': {'type': 'github'}
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

@module.route('/callback/discord')
def authorizedis():
	if request.values.get('error'):
		error = request.values['error']
		print(error)
		return redirect(url_for('Accounts.login'))

	discord = oauth2_session(state=session['oauth2_state'])
	token = discord.fetch_token(module.config['DISCORD_TOKEN_URL'],
		client_secret=module.config['DISCORD_CLIENT_SECRET'],
		authorization_response=request.url)

	session['oauth2_token'] = token

	user = discord_get_user()
	print(user)
	#return str(user)

	try:
		with open(f'data/states/{session["state"]}', 'r') as of:
			st = of.read().strip()
			#print(st == 'register')
			#print(st == 'login')
			of.close()
			os.remove(f'data/states/{session["state"]}')

			if st == 'register':
				if auth.isEmail(user['email']):
					return render_template('core/Accounts/register.html', msg="Account already exists with this email", businessName=files.getBranding()[0])
				userID = auth.getUserCount()
				cf('data/user/{}'.format(userID))
				data = {}
				data['Config'] = []
				data['Config'].append({
				'email': user['email'],
				'password': str(auth.encKey(user['email']).decode()),
				'external': True,
				'ID': userID,
				'secret': str(pyotp.random_base32()),
				'2fa': False,
				'suspended': {'isSuspended': False, 'reason': 'No reason'},
				'type': 'user',
				'args': {'type': 'discord'}
				})
				with open('data/user/{}/config.json'.format(userID), 'w+') as of:
					json.dump(data, of)
				session['user'] = json.dumps(data)
				return redirect(url_for('Accounts.dashboard'))
			if st == 'login':
				#print('login')
				if auth.isEmail(user['email']):
					#return render_template('core/Accounts/register.html', msg="Account already exists with this email", businessName=files.getBranding()[0])
					data = {}
					data['Config'] = []
					data['Config'].append({
					'email': user['email'],
					'password': str(auth.encKey(user['email']).decode()),
					'external': True,
					'ID': auth.getID(user['email'])
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
		print(e)
	return 'Error'

@module.route("/callback/google") # Google Callback
def callback_google():
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
		audience=module.GOOGLE_CLIENT_ID
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
				cf('data/user/{}'.format(userID))
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
	return 'Error'#str(id_info)

@module.route('/dashboard', methods=['GET', 'POST'])
@auth.login_is_required
def dashboard():
	try:
		user = json.loads(json.dumps(auth.isAuth(session['user'])))
		#print(user)
		if user != False:
			for p in user['Config']:
				#print('a')
				return render_template('core/Accounts/dashboard.html', businessName=files.getBranding()[0], email=p['email'])
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(e, exc_type, fname, exc_tb.tb_lineno)
	return redirect(url_for('Accounts.login'))

@module.route('/dashboard/payments', methods=['GET', 'POST'])
@auth.login_is_required
def dashboardPayments():
	try:
		user = json.loads(json.dumps(auth.isAuth(session['user'])))
		#print(user)
		if user != False:
			for p in user['Config']:
				#print('a')
				return render_template('core/Accounts/dashboardPayments.html', businessName=files.getBranding()[0], email=p['email'])
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(e, exc_type, fname, exc_tb.tb_lineno)
	return redirect(url_for('Accounts.login'))

@module.route('/settings', methods=['GET', 'POST'])
@auth.login_is_required
def settings():
	try:
		user = json.loads(json.dumps(auth.isAuth(session['user'])))
		if user != False:
			for p in user['Config']:
				if request.method == 'POST':
					print(request.form)
					if 'gen2FA' in request.form:
						fa = pyotp.totp.TOTP(p['secret'])
						img = qrcode.make(fa.provisioning_uri(name=f'{files.getBranding()[0]} Login', issuer_name=files.getBranding()[0]))
						image_io = BytesIO()
						img.save(image_io, 'PNG')
						dataurl = 'data:image/png;base64,' + b64encode(image_io.getvalue()).decode('ascii')
						return render_template('core/Accounts/settings.html', faenabled=files.readJSONVar('data/user/{}/config.json'.format(p['ID']), '2fa'), qr=dataurl, businessName=files.getBranding()[0], email=p['email'])
					if 'is2FA' in request.form:
						if 'enable-2fa' in request.form:
							files.updateJSON('data/user/{}/config.json'.format(p['ID']), '2fa', True)
						else:
							files.updateJSON('data/user/{}/config.json'.format(p['ID']), '2fa', False)
				return render_template('core/Accounts/settings.html', faenabled=files.readJSONVar('data/user/{}/config.json'.format(p['ID']), '2fa'), businessName=files.getBranding()[0], email=p['email'])
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(e, exc_type, fname, exc_tb.tb_lineno)
	return redirect(url_for('Accounts.login'))

@module.route('/admin/{}'.format(module.name))
@hauth.login_required
def adminPage():
	return render_template('core/Accounts/admin.html', businessName=files.getBranding()[0], moduleName=module.name, moduleDescription=module.moduleDescription)

@module.route('/admin/{}/manageAccounts'.format(module.name))
@hauth.login_required
def adminManageAccounts():
	accs = []
	for f in os.listdir('data/user'):
		try:
			with open(f'data/user/{f}/config.json') as of:
				data = json.load(of)
				accs += [data]
		except Exception as e:
			print(e)
	return render_template('core/Accounts/adminAccounts.html', accounts=accs, businessName=files.getBranding()[0], moduleName=module.name, moduleDescription=module.moduleDescription)

@module.route('/admin/{}/captcha'.format(module.name), methods=['GET', 'POST'])
@hauth.login_required
def adminManageCaptcha():
	if request.method == 'POST':
		print(request.form)
		if 'isEnabled' in request.form:
			if 'hCaptcha-enabled' in request.form:
				files.updateJSON('configs/accounts/hCaptcha.json', 'enabled', True)
				module.config['HCAPTCHA_ENABLED'] = True
			else:
				files.updateJSON('configs/accounts/hCaptcha.json', 'enabled', False)
				module.config['HCAPTCHA_ENABLED'] = False
		if 'siteKey' in request.form:
			files.updateJSON('configs/accounts/hCaptcha.json', 'site_key', request.form['siteKey'])
			module.config['HCAPTCHA_SITE_KEY'] = request.form['siteKey']
		if 'secretKey' in request.form:
			files.updateJSON('configs/accounts/hCaptcha.json', 'secret_key', request.form['secretKey'])
			module.config['HCAPTCHA_SECRET_KEY'] = request.form['secretKey']
	return render_template('core/Accounts/adminManageCaptcha.html', captchaenabled=files.readJSONVar('configs/accounts/hCaptcha.json', 'enabled'), businessName=files.getBranding()[0], moduleName=module.name, moduleDescription=module.moduleDescription)

@module.route('/admin/{}/manageDiscord'.format(module.name), methods=['GET', 'POST'])
@hauth.login_required
def adminManageDiscord():
	if request.method == 'POST':
		print(request.form)
		if 'isEnabled' in request.form:
			if 'discord-enabled' in request.form:
				files.updateJSON('configs/accounts/discord.json', 'enabled', True)
			else:
				files.updateJSON('configs/accounts/discord.json', 'enabled', False)
		if 'clientID' in request.form:
			files.updateJSON('configs/accounts/discord.json', 'client_id', request.form['clientID'])
			module.config['DISCORD_CLIENT_ID'] = request.form['clientID']
		if 'clientSecret' in request.form:
			files.updateJSON('configs/accounts/discord.json', 'client_secret', request.form['clientSecret'])
			module.config['DISCORD_CLIENT_SECRET'] = request.form['clientSecret']
	return render_template('core/Accounts/adminManageDiscord.html', discordenabled=files.readJSONVar('configs/accounts/discord.json', 'enabled'), businessName=files.getBranding()[0], moduleName=module.name, moduleDescription=module.moduleDescription)

@module.route('/admin/{}/manageGithub'.format(module.name), methods=['GET', 'POST'])
@hauth.login_required
def adminManageGithub():
	if request.method == 'POST':
		print(request.form)
		if 'isEnabled' in request.form:
			if 'github-enabled' in request.form:
				files.updateJSON('configs/accounts/github.json', 'enabled', True)
			else:
				files.updateJSON('configs/accounts/github.json', 'enabled', False)
		if 'clientID' in request.form:
			files.updateJSON('configs/accounts/github.json', 'client_id', request.form['clientID'])
		if 'clientSecret' in request.form:
			files.updateJSON('configs/accounts/github.json', 'client_secret', request.form['clientSecret'])
	return render_template('core/Accounts/adminManageGithub.html', githubenabled=files.readJSONVar('configs/accounts/github.json', 'enabled'), businessName=files.getBranding()[0], moduleName=module.name, moduleDescription=module.moduleDescription)


@module.route('/admin/{}/manageGoogle'.format(module.name), methods=['GET', 'POST'])
@hauth.login_required
def adminManageGoogle():
	if request.method == 'POST':
		#print(request.form)
		if 'isEnabled' in request.form:
			if 'google-enabled' in request.form:
				files.updateJSON('configs/accounts/google.json', 'enabled', True)
			else:
				files.updateJSON('configs/accounts/google.json', 'enabled', False)
		if 'clientFile' in request.files:
			if request.files['clientFile'].filename != '':
				request.files['clientFile'].save('configs/accounts/client_secret.json')
				try:
					module.flow = Flow.from_client_secrets_file(
						client_secrets_file='configs/accounts/client_secret.json',
						scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
						redirect_uri=config.domain_url+"callback/google"
					)
				except Exception as e:
					print(f'[{module.name}] Unable to load Google Flow', e)
		if 'clientID' in request.form:
			files.updateJSON('configs/accounts/google.json', 'client_id', request.form['clientID'])
			module.GOOGLE_CLIENT_ID = request.form['clientID']
	return render_template('core/Accounts/adminManageGoogle.html', googleenabled=files.readJSONVar('configs/accounts/google.json', 'enabled'), businessName=files.getBranding()[0], moduleName=module.name, moduleDescription=module.moduleDescription)


checks()
