from django.template import Library

register = Library()

@register.inclusion_tag("projects/topic_item.html")
def show_project_topic(topic):
    return {"topic": topic}

@register.inclusion_tag("projects/project_item.html")
def show_project(project):
    return {"project": project}

@register.inclusion_tag("projects/task_item.html")
def show_task(task):
    return {"task": task}