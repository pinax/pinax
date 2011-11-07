from django import template
from django.conf import settings


register = template.Library()


class SilkNode(template.Node):
    """
    node class for silk tag
    """
    
    def __init__(self, name, attrs):
        self.name = template.Variable(name)
        self.attrs = {}
        for attr in attrs:
            key, value = attr.split("=")
            self.attrs[key] = template.Variable(value)
    
    def render(self, context):
        """
        render the img tag with specified attributes
        """
        name = self.name.resolve(context)
        attrs = []
        for k, v in self.attrs.iteritems():
            attrs.append('%s="%s"' % (k, v.resolve(context)))
        if attrs:
            attrs = " %s" % " ".join(attrs)
        else:
            attrs = ""
        return """<img src="%spinax/img/silk/icons/%s.png"%s />""" % (
            settings.STATIC_URL,
            name,
            attrs,
        )


@register.tag
def silk(parser, token):
    """
    Template tag to render silk icons
    Usage::
    
        {% silk "image_name" arg1="value1" arg2="value2" ... %}
    
    """
    bits = token.split_contents()
    return SilkNode(bits[1], bits[2:])
