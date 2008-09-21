from django import template
from projects.forms import ProjectForm

register = template.Library()

def show_project_topic(topic):
    return {"topic": topic}
register.inclusion_tag("projects/topic_item.html")(show_project_topic)

def show_project(project):
    return {"project": project}
register.inclusion_tag("projects/project_item.html")(show_project)

def show_task(task):
    return {"task": task}
register.inclusion_tag("projects/task_item.html")(show_task)

def do_get_project_form(parser, token):
    try:
        tag_name, as_, context_name = token.split_contents()
    except ValueError:
        tagname = token.contents.split()[0]
        raise template.TemplateSyntaxError, "%(tagname)r tag syntax is as follows: {%% %(tagname)r as VARIABLE %%}" % locals()
    return ProjectFormNode(context_name)

class ProjectFormNode(template.Node):
    def __init__(self, context_name):
        self.context_name = context_name
    def render(self, context):
        context[self.context_name] = ProjectForm()
        return ''

register.tag('get_project_form', do_get_project_form)