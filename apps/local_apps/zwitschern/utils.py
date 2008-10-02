
import random
import zlib
import base64
import urllib2

import twitter


from django.conf import settings

from account.models import other_service

def twitter_account_raw(username, password):
    return twitter.Api(username=username, password=password)

def twitter_account_for_user(user):
    profile = user.get_profile()
    twitter_user = other_service(user, "twitter_user")
    twitter_password = other_service(user, "twitter_password")
    if twitter_user and twitter_password:
        twitter_password = get_twitter_password(settings.SECRET_KEY, twitter_password, decode=True)
        return twitter_account_raw(twitter_user, twitter_password)

def twitter_verify_credentials(account):
    if account is None:
        return False
    url = 'http://twitter.com/account/verify_credentials.json'
    try:
        json = account._FetchUrl(url)
    except account._urllib.HTTPError:
        return False
    return True

def get_twitter_password(key, text, decode=False):
    rand = random.Random(key).randrange
    xortext = lambda text: "".join([chr(ord(c)^rand(256)) for c in text])
    if not decode:
        text = base64.encodestring(xortext(zlib.compress(text)))
    else:
        text = zlib.decompress(xortext(base64.decodestring(text)))
    return text


