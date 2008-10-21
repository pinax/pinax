import re
import urllib2
import gzip
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
try:
    import simplejson
except ImportError:
    from django.utils import simplejson
from django.conf import settings
from django.utils.safestring import mark_safe
from oembed.models import ProviderRule, StoredOEmbed
from django.template.loader import render_to_string

END_OVERRIDES = (')', ',', '.', '>', ']', ';')
MAX_WIDTH = getattr(settings, "OEMBED_MAX_WIDTH", 320)
MAX_HEIGHT = getattr(settings, "OEMBED_MAX_HEIGHT", 240)
FORMAT = getattr(settings, "OEMBED_FORMAT", "json")

def fetch(url, user_agent="django-oembed/0.1"):
    """
    Fetches from a URL, respecting GZip encoding, etc.
    """
    request = urllib2.Request(url)
    request.add_header('User-Agent', user_agent)
    request.add_header('Accept-Encoding', 'gzip')
    opener = urllib2.build_opener()
    f = opener.open(request)
    result = f.read()
    if f.headers.get('content-encoding', '') == 'gzip':
        result = gzip.GzipFile(fileobj=StringIO(result)).read()
    f.close()
    return result

def re_parts(regex_list, text):
    """
    An iterator that returns the entire text, but split by which regex it
    matched, or none at all.  If it did, the first value of the returned tuple
    is the index into the regex list, otherwise -1.

    >>> first_re = re.compile('asdf')
    >>> second_re = re.compile('an')
    >>> list(re_parts([first_re, second_re], 'This is an asdf test.'))
    [(-1, 'This is '), (1, 'an'), (-1, ' '), (0, 'asdf'), (-1, ' test.')]

    >>> list(re_parts([first_re, second_re], 'asdfasdfasdf'))
    [(0, 'asdf'), (0, 'asdf'), (0, 'asdf')]

    >>> list(re_parts([], 'This is an asdf test.'))
    [(-1, 'This is an asdf test.')]

    >>> third_re = re.compile('sdf')
    >>> list(re_parts([first_re, second_re, third_re], 'This is an asdf test.'))
    [(-1, 'This is '), (1, 'an'), (-1, ' '), (0, 'asdf'), (-1, ' test.')]
    """
    def match_compare(x, y):
        return x.start() - y.start()
    prev_end = 0
    iters = [r.finditer(text) for r in regex_list]
    matches = []
    while iters:
        if matches:
            match = matches.pop(0)
            (start, end) = match.span()
            if start > prev_end:
                yield (-1, text[prev_end:start])
                yield (regex_list.index(match.re), text[start:end])
            elif start == prev_end:
                yield (regex_list.index(match.re), text[start:end])
            prev_end = end
        else:
            matches = []
            for iterator in iters:
                try:
                    matches.append(iterator.next())
                except StopIteration:
                    iters.remove(iterator)
            matches = sorted(matches, match_compare)
    last_bit = text[prev_end:]
    if len(last_bit) > 0:
        yield (-1, last_bit)

def replace(text, max_width=MAX_WIDTH, max_height=MAX_HEIGHT):
    """
    Scans a block of text, replacing anything matched by a ``ProviderRule``
    pattern with an OEmbed html snippet, if possible.
    
    Templates should be stored at oembed/{format}.html, so for example:
        
        oembed/video.html
        
    These templates are passed a context variable, ``response``, which is a 
    dictionary representation of the response.
    """
    rules = list(ProviderRule.objects.all())
    patterns = [re.compile(r.regex) for r in rules] # Compiled patterns from the rules
    parts = [] # The parts that we will assemble into the final return value.
    indices = [] # List of indices of parts that need to be replaced with OEmbed stuff.
    indices_rules = [] # List of indices into the rules in order for which index was gotten by.
    urls = set() # A set of URLs to try to lookup from the database.
    stored = {} # A mapping of URLs to StoredOEmbed objects.
    index = 0
    # First we pass through the text, populating our data structures.
    for i, part in re_parts(patterns, text):
        if i == -1:
            parts.append(part)
            index += 1
        else:
            to_append = ""
            # If the link ends with one of our overrides, build a list
            while part[-1] in END_OVERRIDES:
                to_append += part[-1]
                part = part[:-1]
            indices.append(index)
            urls.add(part)
            indices_rules.append(i)
            parts.append(part)
            index += 1
            if to_append:
                parts.append(to_append)
                index += 1
    # Now we fetch a list of all stored patterns, and put it in a dictionary 
    # mapping the URL to to the stored model instance.
    for stored_embed in StoredOEmbed.objects.filter(match__in=urls, max_width=max_width, max_height = max_height):
        stored[stored_embed.match] = stored_embed
    # Now we're going to do the actual replacement of URL to embed.
    for i, id_to_replace in enumerate(indices):
        rule = rules[indices_rules[i]]
        part = parts[id_to_replace]
        try:
            # Try to grab the stored model instance from our dictionary, and
            # use the stored HTML fragment as a replacement.
            parts[id_to_replace] = stored[part].html
        except KeyError:
            try:
                # Build the URL based on the properties defined in the OEmbed spec.
                url = u"%s?url=%s&maxwidth=%s&maxheight=%s&format=%s" % (
                    rule.endpoint, part, max_width, max_height, FORMAT
                )
                # Fetch the link and parse the JSON.
                resp = simplejson.loads(fetch(url))
                # Depending on the embed type, grab the associated template and
                # pass it the parsed JSON response as context.
                replacement = render_to_string('oembed/%s.html' % resp['type'], {'response': resp})
                if replacement:
                    stored_embed = StoredOEmbed.objects.create(
                        match = part,
                        max_width = max_width,
                        max_height = max_height,
                        html = replacement,
                    )
                    stored[stored_embed.match] = stored_embed
                    parts[id_to_replace] = replacement
                else:
                    raise ValueError
            except ValueError:
                parts[id_to_replace] = part
            except KeyError:
                parts[id_to_replace] = part
            except urllib2.HTTPError:
                parts[id_to_replace] = part
    # Combine the list into one string and return it.
    return mark_safe(u''.join(parts))
