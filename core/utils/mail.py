# Add Mail Utils
import smtplib
from email.mime.text import MIMEText
from threading import Thread
from core.utils import files
import config
from uuid import getnode
from cryptography.fernet import Fernet

def sendMailThread(recipient, message, subject):
    if not config.mailEnabled:
        return
    context = None
    dt = files.readJSON('configs/mail/config.json')
    #data = json.loads(dt)
    for p in dt['Config']:
        port = p['port']
        if port == 465:
            context = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL(p['hostname'], port) as server:
                server.ehlo()
                server.login(p['username'], Fernet(getnode().encode()).decrypt(p['password'].encode()))
                msg = '''\
Subject: {}
From: {}

{}
'''.format(subject, p['username'], message)
                server.sendmail(p['username'], recipient, msg)
                print('Sent email')
        except Exception as e:
            print('[Mail] Unable to send email:', e)

def sendMail(recipient, message, subject):
    Thread(target=lambda:sendMailThread(recipient, message, subject)).start()
