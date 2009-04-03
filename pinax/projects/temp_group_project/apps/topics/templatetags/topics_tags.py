from django import template

register = template.Library()

def show_topic(topic):
    return {"topic": topic}
register.inclusion_tag("topics/topic_item.html")(show_topic)