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

def get_repo_name(url: str) -> str:
    last_slash_index = url.rfind("/")
    last_suffix_index = url.rfind(".git")
    if last_suffix_index < 0:
        last_suffix_index = len(url)

    if last_slash_index < 0 or last_suffix_index <= last_slash_index:
        raise Exception("Badly formatted url {}".format(url))

    return url[last_slash_index + 1:last_suffix_index]
