from django import template
from django.conf import settings


register = template.Library()


class IfSettingNode(template.Node):
    
    def __init__(self, nodelist_true, nodelist_false, setting):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.setting = setting
    
    def render(self, context):
        try:
            setting_value = getattr(settings, self.setting)
        except AttributeError:
            return ""
        else:
            if setting_value:
                return self.nodelist_true.render(context)
            else:
                return self.nodelist_false.render(context)
            return ""


@register.tag
def ifsetting(parser, token):
    bits = token.split_contents()
    nodelist_true = parser.parse(("else", "endifsetting"))
    token = parser.next_token()
    
    if token.contents == "else":
        nodelist_false = parser.parse(("endifsetting",))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()
    
    return IfSettingNode(nodelist_true, nodelist_false, bits[1])
    