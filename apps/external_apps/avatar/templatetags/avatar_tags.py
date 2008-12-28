import os.path
import urllib

from django import template
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.hashcompat import md5_constructor

register = template.Library()

AVATAR_GRAVATAR_BACKUP = getattr(settings, 'AVATAR_GRAVATAR_BACKUP', True)
AVATAR_DEFAULT_URL = getattr(settings, 'AVATAR_DEFAULT_URL', 
    settings.MEDIA_URL + os.path.join(os.path.dirname(__file__), 'default.jpg'))

def avatar_url(user, size=80):
    if not isinstance(user, User):
        try:
            user = User.objects.get(username=user)
        except User.DoesNotExist:
            return AVATAR_DEFAULT_URL
    avatars = user.avatar_set.order_by('-date_uploaded')
    primary = avatars.filter(primary=True)
    if primary.count() > 0:
        avatar = primary[0]
    elif avatars.count() > 0:
        avatar = avatars[0]
    else:
        avatar = None
    if avatar is not None:
        if not avatar.thumbnail_exists(size):
            avatar.create_thumbnail(size)
        return avatar.avatar_url(size)
    else:
        if AVATAR_GRAVATAR_BACKUP:
            return "http://www.gravatar.com/avatar/%s/?%s" % (
                md5_constructor(user.email).hexdigest(),
                urllib.urlencode({'s': str(size)}),)
        else:
            return AVATAR_DEFAULT_URL
register.simple_tag(avatar_url)

def avatar(user, size=80):
    if not isinstance(user, User):
        try:
            user = User.objects.get(username=user)
            alt = unicode(user)
            url = avatar_url(user, size)
        except User.DoesNotExist:
            url = AVATAR_DEFAULT_URL
            alt = _("Default Avatar")
    else:
        alt = unicode(user)
        url = avatar_url(user, size)
    return """<img src="%s" alt="%s" />""" % (url, alt)
register.simple_tag(avatar)

def render_avatar(avatar, size=80):
    if not avatar.thumbnail_exists(size):
        avatar.create_thumbnail(size)
    return """<img src="%s" alt="%s" />""" % (
        avatar.avatar_url(size), str(avatar))
register.simple_tag(render_avatar)