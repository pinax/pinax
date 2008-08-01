from django.template import Library

register = Library()

# @@@ for now let's favour DRY over loose coupling and reference tribes
@register.inclusion_tag("tribes/topic_item.html")
def show_project_topic(topic):
    return {"topic": topic}

