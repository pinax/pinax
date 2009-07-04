from django import template

from django_markup.markup import formatter
from django_markup.filter.markdown_filter import MarkdownMarkupFilter
from django_markup.filter.textile_filter import TextileMarkupFilter
from django_markup.filter.rst_filter import RstMarkupFilter


register = template.Library()

# @@@ remove this ASAP
# this code is here to provide a quick backwards compatible interface since
# there are many databases with these old vaules in them.

formatter.register("txl", TextileMarkupFilter)
formatter.register("mrk", MarkdownMarkupFilter)
formatter.register("rst", RstMarkupFilter)