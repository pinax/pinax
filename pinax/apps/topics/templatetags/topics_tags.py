from django import template
from django.contrib.contenttypes.models import ContentType

from topics.models import Topic

register = template.Library()

def show_topic(context, topic):
    return {
        "topic": topic,
        "group": context.get("group"),
    }
register.inclusion_tag("topics/topic_item.html", takes_context=True)(show_topic)

class TopicsForGroupNode(template.Node):
    def __init__(self, group_name, context_name):
        self.group = template.Variable(group_name)
        self.context_name = context_name
    
    def render(self, context):
        try:
            group = self.group.resolve(context)
        except template.VariableDoesNotExist:
            return u''
        content_type = ContentType.objects.get_for_model(group)
        context[self.context_name] = Topic.objects.filter(
            content_type=content_type, object_id=group.id)
        return u''

def do_get_topics_for_group(parser, token):
    """
    Provides the template tag {% get_topics_for_group GROUP as VARIABLE %}
    """
    try:
        _tagname, group_name, _as, context_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(u'%(tagname)r tag syntax is as follows: '
            '{%% %(tagname)r GROUP as VARIABLE %%}' % {'tagname': tagname})
    return TopicsForGroupNode(group_name, context_name)

register.tag('get_topics_for_group', do_get_topics_for_group)