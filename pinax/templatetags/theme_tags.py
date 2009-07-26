from django import template
from django.conf import settings


register = template.Library()


@register.simple_tag
def silk(name):
    return """<img src="%s/pinax/images/silk/icons/%s.png" />""" % (settings.MEDIA_URL, name)
