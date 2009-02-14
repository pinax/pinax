
from django import template
from django.conf import settings

register = template.Library()

class IfSettingNode(template.Node):
    def __init__(self, nodelist, setting):
        self.nodelist = nodelist
        self.setting = setting
        
    def render(self, context):
        try:
            setting_value = getattr(settings, self.setting)
        except AttributeError:
            return ""
        else:
            if setting_value:
                return self.nodelist.render(context)
            return ""

@register.tag
def ifsetting(parser, token):
    bits = token.split_contents()
    nodelist = parser.parse(("endifsetting"))
    parser.delete_first_token()
    return IfSettingNode(nodelist, bits[1])
    