from django import template


register = template.Library()


@register.inclusion_tag("profile_item.html")
def show_profile(user):
    return {"user": user}


@register.simple_tag
def clear_search_url(request):
    getvars = request.GET.copy()
    if "search" in getvars:
        del getvars["search"]
    if len(getvars.keys()) > 0:
        return "%s?%s" % (request.path, getvars.urlencode())
    else:
        return request.path
