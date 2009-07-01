from django import template

from template_utils.markup import formatter
from template_utils.markup import textile, markdown, restructuredtext


register = template.Library()

# @@@ remove this ASAP
# this code is here to provide a quick backwards compatible interface since
# there are many databases with these old vaules in them.

formatter.register("txl", textile)
formatter.register("mrk", markdown)
formatter.register("rst", restructuredtext)