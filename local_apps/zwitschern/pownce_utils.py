import random
import zlib
import base64
import urllib2

import pownce

from django.conf import settings

def pownce_account_raw(username, password):
	return pownce.Api(username, password, 'li6yw8q8ivv8ga9zda28iio4z652377y')

def pownce_account_for_user(user):
	profile = user.get_profile()
	if profile.pownce_user and profile.pownce_password:
		pownce_password = get_pownce_password(settings.SECRET_KEY,profile.pownce_password, decode=True)
		return pownce_account_raw(profile.pownce_user, pownce_password)

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

