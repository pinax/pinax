
from django import template
from django.utils.safestring import mark_safe

from django_openid.models import UserOpenidAssociation

try:
    any
except NameError:
    def any(seq):
        for x in seq:
            if x:
                return True
        return False

register = template.Library()

def openid_icon(openid, user):
    oid = u'%s' % openid
    matches = [u.openid == oid for u in UserOpenidAssociation.objects.filter(user=user)]
    if any(matches):
        return mark_safe(u'<img src="/site_media/openid-icon.png" alt="Logged in with OpenID" />')
    else:
        return u''
register.simple_tag(openid_icon)
