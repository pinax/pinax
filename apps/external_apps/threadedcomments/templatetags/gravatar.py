from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter
from django.utils.encoding import smart_str
from django.utils.safestring import mark_safe
import md5
import urllib

GRAVATAR_MAX_RATING = getattr(settings, 'GRAVATAR_MAX_RATING', 'R')
GRAVATAR_DEFAULT_IMG = getattr(settings, 'GRAVATAR_DEFAULT_IMG', 'img:blank')
GRAVATAR_SIZE = getattr(settings, 'GRAVATAR_SIZE', 80)

GRAVATAR_URL = u'http://www.gravatar.com/avatar.php?gravatar_id=%(hash)s&rating=%(rating)s&size=%(size)s&default=%(default)s'

def get_gravatar_url(parser, token):
    """
    Generates a gravatar image URL based on the given parameters.
        
    Format is as follows (The square brackets indicate that those arguments are 
    optional.)::
    
        {% get_gravatar_url for myemailvar [rating "R" size 80 default img:blank as gravatar_url] %}
    
    Rating, size, and default may be either literal values or template variables.
    The template tag will attempt to resolve variables first, and on resolution
    failure it will use the literal value.
    
    If ``as`` is not specified, the URL will be output to the template in place.
    
    For all other arguments that are not specified, the appropriate default 
    settings attribute will be used instead.
    """
    words = token.contents.split()
    tagname = words.pop(0)
    if len(words) < 2:
        raise template.TemplateSyntaxError, "%r tag: At least one argument should be provided." % tagname
    if words.pop(0) != "for":
        raise template.TemplateSyntaxError, "%r tag: Syntax is {% get_gravatar_url for myemailvar rating "R" size 80 default img:blank as gravatar_url %}, where everything after myemailvar is optional."
    email = words.pop(0)
    if len(words) % 2 != 0:
        raise template.TemplateSyntaxError, "%r tag: Imbalanced number of arguments." % tagname
    args = {
        'email': email,
        'rating': GRAVATAR_MAX_RATING,
        'size': GRAVATAR_SIZE,
        'default': GRAVATAR_DEFAULT_IMG,
    }
    for name, value in zip(words[::2], words[1::2]):
        name = name.lower()
        if name not in ('rating', 'size', 'default', 'as'):
            raise template.TemplateSyntaxError, "%r tag: Invalid argument %r." % tagname, name
        args[smart_str(name)] = value
    return GravatarUrlNode(**args)

class GravatarUrlNode(template.Node):
    def __init__(self, email=None, rating=GRAVATAR_MAX_RATING, size=GRAVATAR_SIZE, 
        default=GRAVATAR_DEFAULT_IMG, **other_kwargs):
        self.email = template.Variable(email)
        self.rating = template.Variable(rating)
        try:
            self.size = template.Variable(size)
        except:
            self.size = size
        self.default = template.Variable(default)
        self.other_kwargs = other_kwargs

    def render(self, context):
        # Try to resolve the variables.  If they are not resolve-able, then use
        # the provided name itself.
        try:
            email = self.email.resolve(context)
        except template.VariableDoesNotExist:
            email = self.email.var
        try:
            rating = self.rating.resolve(context)
        except template.VariableDoesNotExist:
            rating = self.rating.var
        try:
            size = self.size.resolve(context)
        except template.VariableDoesNotExist:
            size = self.size.var
        except AttributeError:
            size = self.size
        try:
            default = self.default.resolve(context)
        except template.VariableDoesNotExist:
            default = self.default.var
        
        gravatargs = {
            'hash': md5.new(email).hexdigest(),
            'rating': rating,
            'size': size,
            'default': urllib.quote_plus(default),
        }
        url = GRAVATAR_URL % gravatargs
        if 'as' in self.other_kwargs:
            context[self.other_kwargs['as']] = mark_safe(url)
            return ''
        return url

def gravatar(email):
    """
    Takes an e-mail address and returns a gravatar image URL, using properties
    from the django settings file.
    """
    hashed_email = md5.new(email).hexdigest()
    return mark_safe(GRAVATAR_URL % {
        'hash': hashed_email,
        'rating': GRAVATAR_MAX_RATING, 
        'size': GRAVATAR_SIZE,
        'default': urllib.quote_plus(GRAVATAR_DEFAULT_IMG),
    })
gravatar = stringfilter(gravatar)


register = template.Library()
register.filter('gravatar', gravatar)
register.tag('get_gravatar_url', get_gravatar_url)
