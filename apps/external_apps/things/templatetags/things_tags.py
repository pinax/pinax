from django import template
from django.core.urlresolvers import reverse

register = template.Library()

def clear_search_url(request):
    getvars = request.GET.copy()
    if 'search' in getvars:
        del getvars['search']
    if len(getvars.keys()) > 0:
        return "%s?%s" % (request.path, getvars.urlencode())
    else:
        return request.path
register.simple_tag(clear_search_url)

def persist_getvars(request):
    getvars = request.GET.copy()
    if len(getvars.keys()) > 0:
        return "?%s" % getvars.urlencode()
    return ''
register.simple_tag(persist_getvars)

def item_url(url_prefix, name_prefix, item):
    try:
        return item.get_absolute_url()
    except AttributeError:
        return reverse('%s_detail' % name_prefix, kwargs={
            'url_prefix': url_prefix,
            'pk': item.pk,
        })
register.simple_tag(item_url)

def display_ordering(context):
    return {
        'fields': context['fields'],
        'field': context['field'],
        'descending': context['descending'],
        'request': context['request'],
    }
register.inclusion_tag('things/ordering.html', takes_context=True)(display_ordering)

def display_search(context):
    return {
        'search_enabled': context['search_enabled'],
        'terms': context['terms'],
        'request': context['request'],
    }
register.inclusion_tag('things/search.html', takes_context=True)(display_search)

def thing_list(name_prefix, url_name):
    return reverse(name_prefix + '_' + url_name + '_list', args=[url_name + '/'])
thing_list = register.simple_tag(thing_list)