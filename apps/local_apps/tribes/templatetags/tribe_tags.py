from django import template
from tribes.forms import TribeForm

register = template.Library()

def show_tribe_topic(topic):
    return {"topic": topic}
register.inclusion_tag("tribes/topic_item.html")(show_tribe_topic)

def show_tribe(tribe):
    return {"tribe": tribe}
register.inclusion_tag("tribes/tribe_item.html")(show_tribe)

def do_get_tribe_form(parser, token):
    try:
        tag_name, as_, context_name = token.split_contents()
    except ValueError:
        tagname = token.contents.split()[0]
        raise template.TemplateSyntaxError, "%(tagname)r tag syntax is as follows: {%% %(tagname)r as VARIABLE %%}" % locals()
    return TribeFormNode(context_name)

class TribeFormNode(template.Node):
    def __init__(self, context_name):
        self.context_name = context_name
    def render(self, context):
        context[self.context_name] = TribeForm()
        return ''

register.tag('get_tribe_form', do_get_tribe_form)