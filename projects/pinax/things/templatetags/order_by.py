from django import template

register = template.Library()

def do_order_by(parser, token):
    split = token.split_contents()
    if len(split) == 4:
        if split[2] == "by":
            return OrderByNode(split[1], split[3])
        else:
            raise template.TemplateSyntaxError('usage is {%% %r x by y %%}' % split[0])
    else:
        raise template.TemplateSyntaxError('usage is {%% %r x by y %%}' % split[0])

class OrderByNode(template.Node):
    def __init__(self, queryset_var, order_field):
        self.queryset_var = template.Variable(queryset_var)
        self.order_field = order_field
        
    def render(self, context):
        key = self.queryset_var.var
        qs = self.queryset_var.resolve(context)
        
        context[key] = qs.order_by(self.order_field)
        return u""

register.tag('order', do_order_by)