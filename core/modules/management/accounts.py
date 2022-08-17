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

from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import facebook_compliance_fix

# OTP Libraries
import pyotp
import qrcode

module = Blueprint('Accounts', __name__)
module.hasAdminPage = True
module.moduleDescription = 'A simple accounts module'
module.version = '1.3'
module.config = {}
# hCaptcha
module.hcaptcha = hCaptcha(module)

#OAuthlib
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # 1 = HTTP / 0 = HTTPS
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = "1" # Used for Microsoft Login

def oauth2_token_updater(token):
    session['oauth2_token'] = token

accmods = {}
accpro = []

for path, dirs, filess in os.walk("core/modules/accounts", topdown=False):
    for fname in filess:
        try:
            name, ext = os.path.splitext(fname)
            if ext == '.py' and not name == '__init__':
                f, filename, descr = imp.find_module(name, [path])
                accmods[fname] = imp.load_module(name, f, filename, descr)
                #print(getattr(mods[fname], 'module').name)
                accpro += [(getattr(accmods[fname], 'module').name, getattr(accmods[fname], 'module'), getattr(accmods[fname], 'oauth2_session'))]
                print(Fore.GREEN + f'[{module.name}] ' + Style.RESET_ALL + 'Imported', accmods[fname].module.name)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Fore.RED, '[ERROR]', path, name, e, exc_type, fname, exc_tb.tb_lineno, Style.RESET_ALL)

famods = {}
fapro = []

for path, dirs, filess in os.walk("core/modules/2fa", topdown=False):
    for fname in filess:
        try:
            name, ext = os.path.splitext(fname)
            if ext == '.py' and not name == '__init__':
                f, filename, descr = imp.find_module(name, [path])
                famods[fname] = imp.load_module(name, f, filename, descr)
                #print(getattr(mods[fname], 'module').name)
                fapro += [(getattr(famods[fname], 'module').name)]
                print(Fore.GREEN + f'[{module.name}] ' + Style.RESET_ALL + 'Imported', famods[fname].module.name)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Fore.RED, '[ERROR]', path, name, e, exc_type, fname, exc_tb.tb_lineno, Style.RESET_ALL)

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
        print(f'[{module.name}] Unable to load hCaptcha settings')
    try:
        for f in os.listdir('data/states'):
            try:
                os.remove(f'data/states/{f}')
            except:
                print(f'[{module.name}] Unable to remove {f} state')
    except Exception as e:
        print(e)
    for f in os.listdir('data/user'):
        cf(f'data/user/{f}/payments')
        cf(f'data/user/{f}/sessions')
        cf(f'data/user/{f}/paydata')

def getActivePro():
    a = []
    for f in accpro:
        try:
            if files.readJSONVar('configs/accounts/{}.json'.format(f[1].basicName), 'enabled'):
                a += [(f[1].basicName, f[1].fontawesome)]
        except:
            pass
    return a

@module.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        for f in request.form:
            try:
                x = f.split('-')
                if x[0] == 'login':
                    for ff in accpro:
                        if ff[1].basicName == x[1]:
                            auth = ff[2](ff[1].config['{}_CLIENT_ID'.format(ff[1].basicName.upper())])
                            try:
                                authorization_url, state = auth.authorization_url(ff[1].config['{}_API_BASE_URL'.format(ff[1].basicName.upper())])
                            except:
                                authorization_url, state = auth.authorization_url()
                            session['oauth2_state'] = state
                            session["state"] = state
                            with open(f'data/states/{state}', 'w+') as of:
                                of.write('login')
                            return redirect(authorization_url)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(e, exc_type, fname, exc_tb.tb_lineno)
        try:
            email = request.form['email']
            password = request.form['password']
        except:
            return render_template('core/Accounts/login.html', msg="Missing an argument", businessName=files.getBranding()[0])
        if module.config['HCAPTCHA_ENABLED']:
            if not module.hcaptcha.verify():
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
            if auth.getUser(auth.getID(email))['Config'][0]['2fa']:
                session['2fa'] = auth.gen2FA(data)
                return redirect(url_for('Accounts.twofa'))
            session['user'] = json.dumps(user)
            return redirect(url_for('Accounts.dashboard'))
        else:
            return render_template('core/Accounts/login.html', msg='Incorrect email or password', businessName=files.getBranding()[0])

    return render_template('core/Accounts/login.html', pros=getActivePro(), businessName=files.getBranding()[0])

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
        for f in request.form:
            try:
                x = f.split('-')
                if x[0] == 'signup':
                    for ff in accpro:
                        if ff[1].basicName == x[1]:
                            auth = ff[2](ff[1].config['{}_CLIENT_ID'.format(ff[1].basicName.upper())])
                            try:
                                authorization_url, state = auth.authorization_url(ff[1].config['{}_API_BASE_URL'.format(ff[1].basicName.upper())])
                            except:
                                authorization_url, state = auth.authorization_url()
                            session['oauth2_state'] = state
                            session["state"] = state
                            with open(f'data/states/{state}', 'w+') as of:
                                of.write('register')
                            return redirect(authorization_url)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(e, exc_type, fname, exc_tb.tb_lineno)
        try:
            email = request.form['email']
            password = request.form['password']
        except:
            return render_template('core/Accounts/register.html', msg="Missing an argument", businessName=files.getBranding()[0])
        if module.config['HCAPTCHA_ENABLED']:
            if not module.hcaptcha.verify():
                return render_template('core/Accounts/register.html', msg="Please retry the Captcha", businessName=files.getBranding()[0])
        if auth.isEmail(email):
            return render_template('core/Accounts/register.html', msg="Account already exists with this email", businessName=files.getBranding()[0])
        userID = auth.getUserCount()
        cf(f'data/user/{userID}')
        cf(f'data/user/{userID}/payments')
        cf(f'data/user/{userID}/sessions')
        cf(f'data/user/{userID}/paydata')
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
    return render_template('core/Accounts/register.html', pros=getActivePro(), businessName=files.getBranding()[0])

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

def getPayments(uid):
    data = {}
    data['Config'] = []
    pi = []
    for f in os.listdir(f'data/user/{uid}/payments'):
        prods = []
        for ff in os.listdir(f'data/user/{uid}/payments/{f}/products'):
            try:
                with open(f'data/user/{uid}/payments/{f}/products/{ff}') as of:
                    data = json.load(of)
                    prods += [data]
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(e, exc_type, fname, exc_tb.tb_lineno)
        pi += [{'id': f, 'prods': prods}]
    print(pi)
    return pi

@module.route('/dashboard/payments', methods=['GET', 'POST'])
@auth.login_is_required
def dashboardPayments():
    try:
        user = json.loads(json.dumps(auth.isAuth(session['user'])))
        #print(user)
        if user != False:
            for p in user['Config']:
                #print('a')
                return render_template('core/Accounts/dashboardPayments.html', payments=getPayments(p['ID']), businessName=files.getBranding()[0], email=p['email'])
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
        #print(request.form)
        if 'isEnabled' in request.form:
            if 'github-enabled' in request.form:
                files.updateJSON('configs/accounts/github.json', 'enabled', True)
            else:
                files.updateJSON('configs/accounts/github.json', 'enabled', False)
        if 'clientID' in request.form:
            files.updateJSON('configs/accounts/github.json', 'client_id', request.form['clientID'])
            module.config['GITHUB_CLIENT_ID'] = request.form['clientID']
        if 'clientSecret' in request.form:
            files.updateJSON('configs/accounts/github.json', 'client_secret', request.form['clientSecret'])
            module.config['GITHUB_CLIENT_SECRET'] = request.form['clientSecret']
    return render_template('core/Accounts/adminManageGithub.html', githubenabled=files.readJSONVar('configs/accounts/github.json', 'enabled'), businessName=files.getBranding()[0], moduleName=module.name, moduleDescription=module.moduleDescription)

@module.route('/admin/{}/manageFacebook'.format(module.name), methods=['GET', 'POST'])
@hauth.login_required
def adminManageFacebook():
    if request.method == 'POST':
        #print(request.form)
        if 'isEnabled' in request.form:
            if 'facebook-enabled' in request.form:
                files.updateJSON('configs/accounts/facebook.json', 'enabled', True)
            else:
                files.updateJSON('configs/accounts/facebook.json', 'enabled', False)
        if 'clientID' in request.form:
            files.updateJSON('configs/accounts/facebook.json', 'client_id', request.form['clientID'])
            module.config['GITHUB_CLIENT_ID'] = request.form['clientID']
        if 'clientSecret' in request.form:
            files.updateJSON('configs/accounts/facebook.json', 'client_secret', request.form['clientSecret'])
            module.config['GITHUB_CLIENT_SECRET'] = request.form['clientSecret']
    return render_template('core/Accounts/adminManageFacebook.html', facebookenabled=files.readJSONVar('configs/accounts/facebook.json', 'enabled'), businessName=files.getBranding()[0], moduleName=module.name, moduleDescription=module.moduleDescription)


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
