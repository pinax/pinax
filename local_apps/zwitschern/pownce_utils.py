import random
import zlib
import base64
import urllib2

import pownce

from django.conf import settings

from account.models import other_service

def pownce_account_raw(username, password):
    # @@@ what is this hard coded key doing here!?!
    return pownce.Api(username, password, 'li6yw8q8ivv8ga9zda28iio4z652377y')

def pownce_account_for_user(user):
    pownce_user = other_service(user, "pownce_user")
    pownce_password = other_service(user, "pownce_password")
    
    if pownce_user and pownce_password:
        pownce_password = get_pownce_password(settings.SECRET_KEY, pownce_password, decode=True)
        return pownce_account_raw(pownce_user, pownce_password)

def pownce_verify_credentials(account):
    try:
        pownce_account = pownce_account_raw(account.username, account.password)
        pownce_account.get_notes(account.username)
        return True
    except:
        return False

def get_pownce_password(key, text, decode=False):
    rand = random.Random(key).randrange
    xortext = lambda text: "".join([chr(ord(c)^rand(256)) for c in text])
    if not decode:
        text = base64.encodestring(xortext(zlib.compress(text)))
    else:
        text = zlib.decompress(xortext(base64.decodestring(text)))
    return text

