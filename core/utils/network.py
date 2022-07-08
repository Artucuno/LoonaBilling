import requests
from threading import Thread

def getChangelog():
    try:
        x = requests.get('https://raw.githubusercontent.com/Loona-cc/LoonaBilling/main/changelog.md', timeout=3)
        return x.text
    except:
        return 'Unable to fetch'

def getVersion():
    try:
        x = requests.get('https://raw.githubusercontent.com/Loona-cc/LoonaBilling/main/version', timeout=3)
        return x.text
    except:
        return 'Unable to fetch'
