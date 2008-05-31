from django import template
from django.utils.html import escape
from django.contrib.auth.models import User

import urllib, hashlib

register = template.Library()

def gravatar(user, size=80):
    if not isinstance(user, User):
        try:
            user = User.objects.get(username=user)
            email = user.email
            username = user.username
        except User.DoesNotExist:
            email = "?"
            username = user
    else:
        email = user.email
        username = user.username
        
    gravatar_url = "http://www.gravatar.com/avatar.php?"
    gravatar_url += urllib.urlencode({'gravatar_id':hashlib.md5(email).hexdigest(), 'size':str(size)})
    return """<img src="%s" alt="gravatar for %s" />""" % (escape(gravatar_url), username)

register.simple_tag(gravatar)