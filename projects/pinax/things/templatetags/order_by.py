from django.template import Library

register = Library()

@register.filter_function
def order_by(obj, args):
    args = [x.strip() for x in args.split(',')]
    return obj.order_by(*args)