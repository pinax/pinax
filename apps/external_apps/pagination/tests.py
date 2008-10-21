"""
>>> from django.core.paginator import Paginator
>>> from pagination.templatetags.pagination_tags import paginate
>>> from django.template import Template, Context

>>> p = Paginator(range(15), 2)
>>> paginate({'paginator': p, 'page_obj': p.page(1)})['pages']
[1, 2, 3, 4, 5, 6, 7, 8]

>>> p = Paginator(range(17), 2)
>>> paginate({'paginator': p, 'page_obj': p.page(1)})['pages']
[1, 2, 3, 4, 5, 6, 7, 8, 9]

>>> p = Paginator(range(19), 2)
>>> paginate({'paginator': p, 'page_obj': p.page(1)})['pages']
[1, 2, 3, 4, None, 7, 8, 9, 10]

>>> p = Paginator(range(21), 2)
>>> paginate({'paginator': p, 'page_obj': p.page(1)})['pages']
[1, 2, 3, 4, None, 8, 9, 10, 11]

# Testing orphans
>>> p = Paginator(range(5), 2, 1)
>>> paginate({'paginator': p, 'page_obj': p.page(1)})['pages']
[1, 2]

>>> p = Paginator(range(21), 2, 1)
>>> paginate({'paginator': p, 'page_obj': p.page(1)})['pages']
[1, 2, 3, 4, None, 7, 8, 9, 10]

>>> t = Template("{% load pagination_tags %}{% autopaginate var 2 %}{% paginate %}")

# WARNING: Please, please nobody read this portion of the code!
>>> class GetProxy(object):
...     def __iter__(self): yield self.__dict__.__iter__
...     def copy(self): return self
...     def urlencode(self): return u''
...     def keys(self): return []
>>> class RequestProxy(object):
...     page = 1
...     GET = GetProxy()
>>>
# ENDWARNING

>>> t.render(Context({'var': range(21), 'request': RequestProxy()}))
u'\\n\\n<div class="pagination">...
>>>
>>> t = Template("{% load pagination_tags %}{% autopaginate var %}{% paginate %}")
>>> t.render(Context({'var': range(21), 'request': RequestProxy()}))
u'\\n\\n<div class="pagination">...
>>>
"""