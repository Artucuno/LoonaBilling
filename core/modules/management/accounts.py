from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
from flask import *
from flask_hcaptcha import hCaptcha
from werkzeug.utils import secure_filename
from core.utils.auth import hauth
from core.utils import auth
#from core.utils.auth import login_is_required
#from core.utils import auth
import config
import sys, os

module = Blueprint('Accounts', __name__)
module.hasAdminPage = True
module.moduleDescription = 'A simple accounts module'
module.version = '1.0'
module.config = {}
module.config['HCAPTCHA_ENABLED'] = False
module.config['HCAPTCHA_SITE_KEY'] = "2e026146-a559-479a-9a68-e9f6110ec6be"
module.config['HCAPTCHA_SECRET_KEY'] = "0xDDC3ef06E5cE9E23eCbFf51625C2b1F0C84a2058"
hcaptcha = hCaptcha(module)

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

@module.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'login-google' in request.form:
            return 'Login with google'
        if 'login-discord' in request.form:
            return 'Login with discord'
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
            print(user)
            print('a')
            session['user'] = json.dumps(user)
            print(session['user'])
            return redirect(url_for('Accounts.dashboard'))
        else:
            return render_template('core/Accounts/login.html', msg='Incorrect email or password', businessName=config.businessName)

    return render_template('core/Accounts/login.html', businessName=config.businessName)

@module.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if 'signup-google' in request.form:
            return 'Signup with google'
        if 'signup-discord' in request.form:
            return 'Signup with discord'
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
        data = {
        'email': email,
        'password': str(auth.encKey(password).decode()),
        'external': False,
        'ID': userID,
        'args': {}
        }
        with open('data/user/{}/config.json'.format(userID), 'w+') as of:
            json.dump(data, of)
        session['user'] = json.dumps(data)

        return redirect(url_for('Accounts.dashboard'))
    return render_template('core/Accounts/register.html', businessName=config.businessName)

@module.route('/logout', methods=['GET', 'POST'])
def logout():
    try:
        session.clear()
        #session.pop('user', None)
    except Exception as e:
        print(e)
    return redirect(url_for('Accounts.login'))

@auth.login_is_required
@module.route('/dashboard', methods=['GET', 'POST'])
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
