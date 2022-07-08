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

from core.utils.auth import hauth
from core.utils import auth
from core.utils import files

from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized

module = Blueprint('Accounts', __name__)
module.hasAdminPage = True
module.moduleDescription = 'A simple accounts module'
module.version = '1.1'
module.config = {}
# hCaptcha
module.config['HCAPTCHA_ENABLED'] = False
module.config['HCAPTCHA_SITE_KEY'] = ""
module.config['HCAPTCHA_SECRET_KEY'] = ""
# Google Login
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
# Discord Login
#os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"      # !! Only in development environment.
#module.config["DISCORD_CLIENT_ID"] =     # Discord client ID.
#module.config["DISCORD_CLIENT_SECRET"] = ""                # Discord client secret.
#module.config["DISCORD_REDIRECT_URI"] = config.domain_url+"callback/discord"                 # URL to your callback endpoint.

hcaptcha = hCaptcha(module)
#discord = DiscordOAuth2Session(module)

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
    cf('configs/accounts')
    if not os.path.isfile('configs/accounts/google.json'):
        data = {}
        data['Config'] = []
        data['Config'].append({
        'enabled': True,
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


@module.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'login-google' in request.form:
            authorization_url, state = module.flow.authorization_url()  #asking the flow class for the authorization (login) url
            session["state"] = state
            with open(f'data/states/{state}', 'w+') as of:
                of.write('login')
            return redirect(authorization_url)
        #if 'login-discord' in request.form:
        #    return discord.create_session()
        try:
            email = request.form['email']
            password = request.form['password']
        except:
            return render_template('core/Accounts/login.html', msg="Missing an argument", businessName=files.getBranding()[0])
        if module.config['HCAPTCHA_ENABLED']:
            if not hcaptcha.verify():
                return render_template('core/Accounts/login.html', msg="Please retry the Captcha", businessName=files.getBranding()[0])
        #if auth.isEmail(email):
        #    return render_template('core/Accounts/login.html', msg="Account already exists with this email", businessName=files.getBranding()[0])
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
            session['user'] = json.dumps(user)
            return redirect(url_for('Accounts.dashboard'))
        else:
            return render_template('core/Accounts/login.html', msg='Incorrect email or password', businessName=files.getBranding()[0])

    return render_template('core/Accounts/login.html', businessName=files.getBranding()[0])

@module.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if 'signup-google' in request.form:
            authorization_url, state = module.flow.authorization_url()  #asking the flow class for the authorization (login) url
            session["state"] = state
            with open(f'data/states/{state}', 'w+') as of:
                of.write('register')
            return redirect(authorization_url)
        #if 'signup-discord' in request.form:
        #    state = auth.genState()
        #    session['state'] = state
        #    open(f'data/states/{state}', 'w+').write('register')
        #    return discord.create_session()
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
        'suspended': {'isSuspended': False, 'reason': 'No reason'},
        'args': {}
        })
        with open('data/user/{}/config.json'.format(userID), 'w+') as of:
            json.dump(data, of)
        session['user'] = json.dumps(data)

        return redirect(url_for('Accounts.dashboard'))
    return render_template('core/Accounts/register.html', businessName=files.getBranding()[0])

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

#@module.route("/callback/discord")
#def callback_discord():
#    discord.callback()
#    return redirect(url_for(".me"))

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
                    return 'Invalid email'
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

@module.route('/admin/{}'.format(module.name))
@hauth.login_required
def adminPage():
    return render_template('core/Accounts/admin.html', businessName=files.getBranding()[0], moduleName=module.name, moduleDescription=module.moduleDescription)

@module.route('/admin/{}/manageGoogle'.format(module.name), methods=['GET', 'POST'])
@hauth.login_required
def adminManageGoogle():
    if request.method == 'POST':
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
    return render_template('core/Accounts/adminManageGoogle.html', businessName=files.getBranding()[0], moduleName=module.name, moduleDescription=module.moduleDescription)


checks()
