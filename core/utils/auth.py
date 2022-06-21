import base64
from uuid import getnode
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

def encKey(adPass):
    password = adPass.encode()
    salt = str(getnode()).encode()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key

@auth.verify_password
def verify_password(username, password):
    users = {
        "admin": open('setup', 'rb').read(),
    }
    print(str(users['admin']))
    print(str(encKey(password)))
    print(users["admin"] == encKey(password))
    if username in users and users["admin"] == encKey(password):
        return username
