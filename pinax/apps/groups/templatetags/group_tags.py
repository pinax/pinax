from django import template
from django.utils.encoding import smart_str
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db.models import get_model
from django.db.models.query import QuerySet


register = template.Library()


class GroupURLNode(template.Node):
    def __init__(self, view_name, group, kwargs, asvar):
        self.view_name = view_name
        self.group = group
        self.kwargs = kwargs
        self.asvar = asvar
    
    def render(self, context):
        url = ""
        group = self.group.resolve(context)
        
        kwargs = {}
        for k, v in self.kwargs.items():
            kwargs[smart_str(k, "ascii")] = v.resolve(context)
        
        if group:
            bridge = group.content_bridge
            try:
                url = bridge.reverse(self.view_name, group, kwargs=kwargs)
            except NoReverseMatch:
                if self.asvar is None:
                    raise
        else:
            try:
                url = reverse(self.view_name, kwargs=kwargs)
            except NoReverseMatch:
                if self.asvar is None:
                    raise
                
        if self.asvar:
            context[self.asvar] = url
            return ""
        else:
            return url


class ContentObjectsNode(template.Node):
    def __init__(self, group_var, model_name_var, context_var):
        self.group_var = template.Variable(group_var)
        self.model_name_var = template.Variable(model_name_var)
        self.context_var = context_var
    
    def render(self, context):
        group = self.group_var.resolve(context)
        model_name = self.model_name_var.resolve(context)
        
        if isinstance(model_name, QuerySet):
            model = model_name
        else:
            app_name, model_name = model_name.split(".")
            model = get_model(app_name, model_name)
        
        context[self.context_var] = group.content_objects(model)
        return ""


@register.tag
def groupurl(parser, token):
    bits = token.contents.split()
    tag_name = bits[0]
    if len(bits) < 3:
        raise template.TemplateSyntaxError("'%s' takes at least two arguments"
            " (path to a view and a group)" % tag_name)
    
    view_name = bits[1]
    group = parser.compile_filter(bits[2])
    args = []
    kwargs = {}
    asvar = None
    
    if len(bits) > 3:
        bits = iter(bits[3:])
        for bit in bits:
            if bit == "as":
                asvar = bits.next()
                break
            else:
                for arg in bit.split(","):
                    if "=" in arg:
                        k, v = arg.split("=", 1)
                        k = k.strip()
                        kwargs[k] = parser.compile_filter(v)
                    elif arg:
                        raise template.TemplateSyntaxError("'%s' does not support non-kwargs arguments." % tag_name)
    
    return GroupURLNode(view_name, group, kwargs, asvar)


@register.tag
def content_objects(parser, token):
    """
        {% content_objects group "tasks.Task" as tasks %}
    """
    bits = token.split_contents()
    if len(bits) != 5:
        raise template.TemplateSyntaxError("'%s' requires five arguments." % bits[0])
    return ContentObjectsNode(bits[1], bits[2], bits[4])
