from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
from flask import *
from flask_hcaptcha import hCaptcha
from werkzeug.utils import secure_filename
from core.utils.auth import hauth
from core.utils import auth
import pathlib
import requests
import config
import sys, os

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
GOOGLE_CLIENT_ID = ""
client_secrets_file = "client_secret.json"
# Discord Login
#os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"      # !! Only in development environment.
#module.config["DISCORD_CLIENT_ID"] =     # Discord client ID.
#module.config["DISCORD_CLIENT_SECRET"] = ""                # Discord client secret.
#module.config["DISCORD_REDIRECT_URI"] = config.domain_url+"callback/discord"                 # URL to your callback endpoint.

try:
    flow = Flow.from_client_secrets_file(
        client_secrets_file=client_secrets_file,
        scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
        redirect_uri=config.domain_url+"callback/google"
    )
except:
    pass

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

@module.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'login-google' in request.form:
            authorization_url, state = flow.authorization_url()  #asking the flow class for the authorization (login) url
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
            return render_template('core/Accounts/login.html', msg="Missing an argument", businessName=config.businessName)
        if module.config['HCAPTCHA_ENABLED']:
            if not hcaptcha.verify():
                return render_template('core/Accounts/login.html', msg="Please retry the Captcha", businessName=config.businessName)
        #if auth.isEmail(email):
        #    return render_template('core/Accounts/login.html', msg="Account already exists with this email", businessName=config.businessName)
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
            return redirect(config.domain_url+'dashboard')
        else:
            return render_template('core/Accounts/login.html', msg='Incorrect email or password', businessName=config.businessName)

    return render_template('core/Accounts/login.html', businessName=config.businessName)

@module.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if 'signup-google' in request.form:
            authorization_url, state = flow.authorization_url()  #asking the flow class for the authorization (login) url
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
            return render_template('core/Accounts/register.html', msg="Missing an argument", businessName=config.businessName)
        if module.config['HCAPTCHA_ENABLED']:
            if not hcaptcha.verify():
                return render_template('core/Accounts/register.html', msg="Please retry the Captcha", businessName=config.businessName)
        if auth.isEmail(email):
            return render_template('core/Accounts/register.html', msg="Account already exists with this email", businessName=config.businessName)
        userID = auth.getUserCount()
        cf('data/user/{}'.format(userID))
        data = {}
        data['Config'] = []
        data['Config'].append({
        'email': email,
        'password': str(auth.encKey(password).decode()),
        'external': False,
        'ID': userID,
        'suspended': {'isSuspended': False, 'reason': 'No reason'},
        'args': {}
        })
        with open('data/user/{}/config.json'.format(userID), 'w+') as of:
            json.dump(data, of)
        session['user'] = json.dumps(data)

        return redirect(config.domain_url+'dashboard')
    return render_template('core/Accounts/register.html', businessName=config.businessName)

@module.route('/suspended')
def suspended():
    return 'Account suspended.'

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
    flow.fetch_token(authorization_response=request.url)
    #print(session['state'])

    if not session["state"] == request.args["state"]:
        abort(500)  #state does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )
    #print(id_info)
    try:
        with open(f'data/states/{session["state"]}', 'r') as of:
            st = of.read().strip()
            #print(st == 'register')
            #print(st == 'login')

            if st == 'register':
                if auth.isEmail(id_info['email']):
                    return render_template('core/Accounts/register.html', msg="Account already exists with this email", businessName=config.businessName)
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
                'args': {'type': 'google'}
                })
                with open('data/user/{}/config.json'.format(userID), 'w+') as of:
                    json.dump(data, of)
                session['user'] = json.dumps(data)
                return redirect(config.domain_url+'dashboard')
            if st == 'login':
                #print('login')
                if auth.isEmail(id_info['email']):
                    #return render_template('core/Accounts/register.html', msg="Account already exists with this email", businessName=config.businessName)
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
                        return redirect(config.domain_url+'dashboard')
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
                return render_template('core/Accounts/dashboard.html', businessName=config.businessName, email=p['email'])
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(e, exc_type, fname, exc_tb.tb_lineno)
    return redirect(url_for('Accounts.login'))

@module.route('/admin/{}'.format(module.name))
@hauth.login_required
def adminPage():
    return render_template('core/Stripe/admin.html', businessName=config.businessName, moduleName=module.name, moduleDescription=module.moduleDescription)

checks()
