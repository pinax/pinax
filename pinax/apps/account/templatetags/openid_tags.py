from django import template
from django.core.exceptions import ImproperlyConfigured

from pinax.apps.account.utils import has_openid


register = template.Library()


class IfOpenidNode(template.Node):
    
    def __init__(self, nodelist_true, nodelist_false):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
    
    def render(self, context):
        try:
            request = context["request"]
        except KeyError:
            raise ImproperlyConfigured(
                "You must enable 'django.core.context_processors.request' in "
                "TEMPLATE_CONTEXT_PROCESSORS"
            )
        if has_openid(request):
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)
        return u""


@register.tag
def ifopenid(parser, token):
    nodelist_true = parser.parse(("else", "endifopenid"))
    token = parser.next_token()
    if token.contents == "else":
        nodelist_false = parser.parse(("endifopenid",))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()
    return IfOpenidNode(nodelist_true, nodelist_false)
