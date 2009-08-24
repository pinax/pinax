from django import template

from django.contrib.contenttypes.models import ContentType

from django.core.urlresolvers import reverse
from django.conf import settings

from tagging.models import Tag, TaggedItem
from tagging.utils import parse_tag_input

from tasks.models import Task

import re

register = template.Library()
task_contenttype = ContentType.objects.get(app_label='tasks', model='task')

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

@register.inclusion_tag("tasks/tag_list.html")
def task_tags(obj, group=None):
    taglist = parse_tag_input(obj.tags)
    return {
        "tags": taglist,
        "group": group,
    }

class TasksForTagNode(template.Node):
    def __init__(self, tag, var_name, selection):
        self.tag = tag
        self.var_name = var_name
        self.selection = selection

    def render(self, context):
        try:
            tag = template.Variable(self.tag).resolve(context)
        except:
            tag = self.tag
        
        try:
            selection = template.Variable(self.selection).resolve(context)
        except:
            selection = Task.objects.all()
        
        try:
            tasks = selection.filter(id__in=[i[0] for i in TaggedItem.objects.filter(tag__name=str(tag),content_type=task_contenttype).values_list('object_id')])
        except:
            return ''
        
        context[self.var_name] = tasks
        return ''

@register.tag(name='tasks_for_tag')
def tasks_for_tag(parser, token):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]

    m = re.search(r'(\w+) as (\w+) in (\w+)', arg)
    if not m:
        m = re.search(r'(\w+) as (\w+)', arg)
        if not m:
            raise template.TemplateSyntaxError, "%r tag had invalid arguments" % tag_name

    tag = m.groups()[0]
    var_name = m.groups()[1]
    try:
        selection = m.groups()[2]
    except IndexError:
        selection = None

    return TasksForTagNode(tag, var_name, selection)

@register.filter
def simple_linebreak(text):
    # TODO: replace with better tooltip feature or detail page
    return '<br />'.join(text.splitlines())
    