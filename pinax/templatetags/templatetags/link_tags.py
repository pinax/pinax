from django import template


register = template.Library()


@register.simple_tag
def fk_field(obj):
    if obj:
        return """<a href="%s">%s</a>""" % (obj.get_absolute_url(), obj)
    else:
        return ""


@register.simple_tag
def mail_field(value):
    if value:
        return """<a href="mailto:%s">%s</a>""" % (value, value)
    else:
        return ""
