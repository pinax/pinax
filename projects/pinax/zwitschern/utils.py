
import random
import zlib
import base64
import urllib2

import twitter

from django.conf import settings

def twitter_account_raw(username, password):
    if username and password:
        twitter_password = get_twitter_password(settings.SECRET_KEY,
            password, reverse=True)
        return twitter.Api(username=username, password=twitter_password)

def twitter_account_for_user(user):
    profile = user.get_profile()
    return twitter_account_raw(profile.twitter_user, profile.twitter_password)

def twitter_verify_credentials(account):
    if account is None:
        return False
    url = 'http://twitter.com/account/verify_credentials.json'
    try:
        json = account._FetchUrl(url)
    except account._urllib.HTTPError:
        return False
    return True

def get_twitter_password(key, text, reverse=False):
    rand = random.Random(key).randrange
    xortext = lambda text : ''.join([chr(ord(elem)^rand(256)) for elem in text])
    if not reverse:
        text = base64.encodestring(xortext(zlib.compress(text)))
    if reverse:
        text = zlib.decompress(xortext(base64.decodestring(text)))
    return text

