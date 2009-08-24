from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def silk(name):
    return """<img src="%spinax/images/silk/icons/%s.png" />""" % (settings.STATIC_URL, name)
