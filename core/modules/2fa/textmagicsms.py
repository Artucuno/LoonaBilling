from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound


module = Blueprint('TextMagic-SMS', __name__)
module.hasAdminPage = False
module.moduleDescription = '2FA and SMS Sending Module'
module.version = '1.0'

# Soon

#username = "your_textmagic_username"
#token = "your_apiv2_key"
#client = TextmagicRestClient(username, token)
#message = client.messages.create(phones="9990001001", text="Hello TextMagic")
