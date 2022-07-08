# Add Mail Utils
import smtplib
from email.mime.text import MIMEText
from threading import Thread

def sendMailThread(port, message):
    context = None
    if port == 465:
        context = ssl.create_default_context()

    with smtplib.SMTP_SSL("", port, context=context) as server:
        server.login("my@gmail.com", password)

def sendMail(port, message):
    Thread(target=lambda:sendMailThread(port, message)).start()
