from django import template
from newprojects.forms import ProjectForm

register = template.Library()

def do_get_project_form(parser, token):
    try:
        tag_name, _, context_name = token.split_contents()
    except ValueError:
        tagname = token.contents.split()[0]
        raise (template.TemplateSyntaxError,
                ("%(tagname)r tag syntax is as follows: "
                    "{%% %(tagname)r as VARIABLE %%}" % {'tagname': tagname}))
    return ProjectFormNode(context_name)

class ProjectFormNode(template.Node):
    def __init__(self, context_name):
        self.context_name = context_name
    def render(self, context):
        context[self.context_name] = ProjectForm()
        return ''

register.tag('get_project_form', do_get_project_form)


@register.inclusion_tag("newprojects/project_item.html", takes_context=True)
def show_project(context, project):
    return {'project': project, 'request': context['request']}

# @@@ should move these next two as they aren't particularly project-specific

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