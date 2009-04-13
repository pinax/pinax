from django import template
from newtribes.forms import TribeForm

register = template.Library()

def do_get_tribe_form(parser, token):
    try:
        tag_name, _, context_name = token.split_contents()
    except ValueError:
        tagname = token.contents.split()[0]
        raise (template.TemplateSyntaxError,
                ("%(tagname)r tag syntax is as follows: "
                    "{%% %(tagname)r as VARIABLE %%}" % {'tagname': tagname}))
    return TribeFormNode(context_name)

class TribeFormNode(template.Node):
    def __init__(self, context_name):
        self.context_name = context_name
    def render(self, context):
        context[self.context_name] = TribeForm()
        return ''

register.tag('get_tribe_form', do_get_tribe_form)


@register.inclusion_tag("newtribes/tribe_item.html", takes_context=True)
def show_tribe(context, tribe):
    return {'tribe': tribe, 'request': context['request']}

# @@@ should move these next two as they aren't particularly tribe-specific

@register.simple_tag
def clear_search_url(request):
    getvars = request.GET.copy()
    if 'search' in getvars:
        del getvars['search']
    if len(getvars.keys()) > 0:
        return "%s?%s" % (request.path, getvars.urlencode())
    else:
        return request.path


@register.simple_tag
def persist_getvars(request):
    getvars = request.GET.copy()
    if len(getvars.keys()) > 0:
        return "?%s" % getvars.urlencode()
    return ''