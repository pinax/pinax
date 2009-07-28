import re
from django import template
#from photologue.utils import EXIF
register = template.Library()

@register.tag(name="print_exif")
def do_print_exif(parser, token):
    try:
        tag_name, exif = token.contents.split()
    except ValueError:
        msg = '%r tag requires a single argument' % token.contents[0]
        raise template.TemplateSyntaxError(msg)

    exif = parser.compile_filter(exif)
    return PrintExifNode(exif)

class PrintExifNode(template.Node):

    def __init__(self, exif):

        self.exif = exif

    def render(self, context):
        try:
            exif = unicode(self.exif.resolve(context, True))
        except template.VariableDoesNotExist:
            exif = u''

        EXPR =  "'(?P<key>[^:]*)'\:(?P<value>[^,]*),"
        expr = re.compile(EXPR)
        msg  = "<table>"
        for i in expr.findall(exif):
            msg += "<tr><td>%s</td><td>%s</td></tr>" % (i[0],i[1])

        msg += "</table>"

        return u'<div id="exif">%s</div>' % (msg)

