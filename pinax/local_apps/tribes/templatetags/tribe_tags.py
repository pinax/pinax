from django.template import Library

register = Library()

@register.inclusion_tag("tribes/topic_item.html")
def show_tribe_topic(topic):
    return {"topic": topic}

@register.inclusion_tag("tribes/tribe_item.html")
def show_tribe(tribe):
    return {"tribe": tribe}
