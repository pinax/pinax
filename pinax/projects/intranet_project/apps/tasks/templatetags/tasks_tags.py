from django import template

from django.core.urlresolvers import reverse
from django.conf import settings

from tagging.models import Tag

register = template.Library()

@register.inclusion_tag("tasks/task_item.html")
def show_task(task):
    return {
        "task": task,
        "MEDIA_URL": settings.MEDIA_URL,
    }

@register.simple_tag
def focus_url(field, value):
    if field is None:
        field = "modified"
    if field == "assignee" and value == None:
        value = "unassigned"
    return reverse("task_focus", args=[field, value])

@register.inclusion_tag("tasks/tag_list.html")
def task_tags(obj):
    tags = Tag.objects.get_for_object(obj).order_by("name")
    return {
        "tags": tags,
    }
