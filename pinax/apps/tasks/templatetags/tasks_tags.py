import re

from django import template
from django.conf import settings
from django.core.urlresolvers import reverse

from django.contrib.contenttypes.models import ContentType

from pinax.apps.tasks.models import Task


register = template.Library()


@register.inclusion_tag("tasks/task_item.html", takes_context=True)
def show_task(context, task, nudge):
    return {
        "nudge": nudge,
        "task": task,
        "MEDIA_URL": settings.MEDIA_URL,
        "STATIC_URL": settings.STATIC_URL,
        "group": context["group"],
    }


@register.simple_tag
def focus_url(field, value, group=None):
    if field is None:
        field = "modified"
    if field == "assignee" and value == None:
        value = "unassigned"
    kwargs = {"field": field, "value": value}
    if group is None:
        return reverse("task_focus", kwargs=kwargs)
    else:
        return group.content_bridge.reverse("task_focus", group, kwargs=kwargs)


class TasksForTagNode(template.Node):
    def __init__(self, tag, var_name):
        self.tag = tag
        self.var_name = var_name
    
    def render(self, context):
        try:
            tag = template.Variable(self.tag).resolve(context)
        except:
            tag = self.tag
        
        try:
            tasks = Task.objects.filter(tags__name__in = [str(tag), ])
        except:
            return ""
        
        context[self.var_name] = tasks
        return ""


@register.tag(name="tasks_for_tag")
def tasks_for_tag(parser, token):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]
    
    m = re.search(r"(\w+) as (\w+)", arg)
    if not m:
        raise template.TemplateSyntaxError, "%r tag had invalid arguments" % tag_name
    
    tag = m.groups()[0]
    var_name = m.groups()[1]
    
    return TasksForTagNode(tag, var_name)


@register.filter
def simple_linebreak(text):
    # TODO: replace with better tooltip feature or detail page
    return "<br />".join(text.splitlines())
