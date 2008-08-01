from django.template import Library

register = Library()

@register.inclusion_tag("tag_app/tag_list.html")
def show_tags_for(obj):
    return {"obj": obj}