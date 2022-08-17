from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
import requests
from threading import Thread

module = Blueprint('Android SMS', __name__)
module.hasAdminPage = False
module.moduleDescription = '2FA and SMS Sending Module'
module.version = '1.0'

def sendSMS(phone, sms):
    x = requests.post('https://192.168.137.14:8080/sendSMS', data={'phone': str(phone), 'message': sms, 'password': 'amogus'}, verify=False)
    print(x.text)

#for f in range(10):
#    Thread(target=lambda:sendSMS('', 'monke')).start()
