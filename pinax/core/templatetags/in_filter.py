from django import template

register = template.Library()

# http://www.djangosnippets.org/snippets/379/

@register.filter
def in_list(value, arg):
    """
    Tests if value is in arg.
    """
    return value in arg
