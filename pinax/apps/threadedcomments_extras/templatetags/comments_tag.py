from django import template



register = template.Library()



@register.inclusion_tag("threadedcomments/comments.html", takes_context=True)
def comments(context, obj):
    return {
        "object": obj,
        "request": context["request"],
        "user": context["user"],
    }
