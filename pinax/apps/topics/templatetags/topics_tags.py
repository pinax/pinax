from django import template

from django.contrib.contenttypes.models import ContentType

from pinax.apps.topics.models import Topic



register = template.Library()



@register.inclusion_tag("topics/topic_item.html", takes_context=True)
def show_topic(context, topic):
    return {
        "topic": topic,
        "group": context.get("group"),
    }


class TopicsForGroupNode(template.Node):
    
    def __init__(self, group_name, context_name):
        self.group = template.Variable(group_name)
        self.context_name = context_name
    
    def render(self, context):
        try:
            group = self.group.resolve(context)
        except template.VariableDoesNotExist:
            return u""
        content_type = ContentType.objects.get_for_model(group)
        context[self.context_name] = Topic.objects.filter(
            content_type=content_type, object_id=group.id)
        return u""


@register.tag(name="get_topics_for_group")
def do_get_topics_for_group(parser, token):
    """
    Provides the template tag {% get_topics_for_group GROUP as VARIABLE %}
    """
    try:
        _tagname, group_name, _as, context_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(u"""get_topics_for_group tag syntax is as follows: 
            {%% get_topics_for_group GROUP as VARIABLE %%}""")
    return TopicsForGroupNode(group_name, context_name)
