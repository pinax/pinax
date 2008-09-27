from django import template
from account.models import OtherServiceInfo

register = template.Library()

def other_service(user, key):
    try:
        value = OtherServiceInfo.objects.get(user=user, key=key).value
    except OtherServiceInfo.DoesNotExist:
        value = u""
    return value
register.simple_tag(other_service)