import requests
from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
from flask import *

module = Blueprint('DiscordWebhook', __name__)
module.hasAdminPage = False
module.moduleDescription = 'Automate simple Discord Webhook requests'
module.version = '1.0'
module.methods = dir()

module.automation = [('sendHook', {'url': 'str', 'username': 'str', 'text': 'str'})]

def sendHook(dta):
    url = dta[0]
    username = dta[1]
    text= dta[2]

    #for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
    data = {
        "content" : text,
        "username" : username,
    }

    result = requests.post(url, json = data)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
