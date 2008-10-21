from django import template
from django.conf import settings
from django.core.cache import cache
from cPickle import loads, dumps, HIGHEST_PROTOCOL
import datetime
import feedparser
import re
import time

def _getdefault(name, default=None):
    try:
        default = getattr(settings, name)
    except: pass
    return default

FEEDUTIL_NUM_POSTS = _getdefault('FEEDUTIL_NUM_POSTS', -1)
FEEDUTIL_CACHE_MIN = _getdefault('FEEDUTIL_CACHE_MIN', 30)
FEEDUTIL_SUMMARY_LEN = _getdefault('FEEDUTIL_SUMMARY_LEN', 150)
FEEDUTIL_SUMMARY_HTML_WORDS =  _getdefault('FEEDUTIL_SUMMARY_HTML_WORDS', 25)

register = template.Library()

def summarize(text):
    cleaned = template.defaultfilters.striptags(text)
    l = len(cleaned)
    if len(cleaned) > FEEDUTIL_SUMMARY_LEN:
        cleaned = cleaned[:FEEDUTIL_SUMMARY_LEN] + '...'
    return cleaned

def summarize_html(text):
    return template.defaultfilters.truncatewords_html(text,
                            FEEDUTIL_SUMMARY_HTML_WORDS) + ' ...'

def pull_feed(feed_url, posts_to_show=None, cache_expires=None):
    if posts_to_show is None: posts_to_show = FEEDUTIL_NUM_POSTS
    if cache_expires is None: cache_expires = FEEDUTIL_CACHE_MIN
    cachename = 'feed_cache_' + template.defaultfilters.slugify(feed_url)
    posts = []
    data = None
    if cache_expires > 0:
        data = cache.get(cachename)
    if data is None:
        # load feed
        try:
            feed = feedparser.parse(feed_url)
            entries = feed['entries']
            #if posts_to_show > 0 and len(entries) > posts_to_show:
            #    entries = entries[:posts_to_show]
            posts = [ {
                'title': entry.title,
                'author': entry.author if entry.has_key('author') else '',
                'summary': summarize(entry.summary if entry.has_key('summary') else entry.content[0]['value']),
                'summary_html': summarize_html(entry.description if entry.has_key('description') else entry.content[0]['value']),
                'content': entry.description if entry.has_key('description') else entry.content[0]['value'],
                'url': entry.link,
                'comments': entry.comments if entry.has_key('comments') else '',
                'published': datetime.datetime.fromtimestamp(time.mktime(entry.updated_parsed)) if entry.has_key('updated_parsed') else '', }
                        for entry in entries ]
        except:
            if settings.DEBUG:
                raise
            return []
        if cache_expires > 0:
            cache.set(cachename, posts, cache_expires*60)
    else:
        #load feed from cache
        posts = data

    if posts_to_show > 0 and len(posts) > posts_to_show:
        posts = posts[:posts_to_show]

    return posts

@register.inclusion_tag('feedutil/feed.html')
def feed(feed_url, posts_to_show=None, cache_expires=None):
    """
    Render an RSS/Atom feed using the 'feedutil/feed.html' template.

    ::
        {% feed feed_url [posts_to_show] [cache_expires] %}
        {% feed "https://foo.net/timeline?max=5&format=rss" 5 60 %}


    feed_url:      full url to the feed (required)
    posts_to_show: Number of posts to pull. <=0 for all
                   (default: settings.FEEDUTIL_NUM_POSTS or -1)
    cache_expired: Number of minuites for the cache. <=0 for no cache.
                   (default: settings.FEEDUTIL_CACHE_MIN or 30)

    """
    return { 'posts': pull_feed(feed_url, posts_to_show, cache_expires) }

class GetFeedNode(template.Node):
    def __init__(self, var_name, feed_url, posts_to_show=None,
                 cache_expires=None):
        self.var_name = var_name
        self.feed_url = feed_url
        self.posts_to_show = posts_to_show
        self.cache_expires = cache_expires
    def render(self, context):
        posts_to_show = cache_expires = None
        try:
            feed_url = template.resolve_variable(self.feed_url, context)
        except:
            if settings.DEBUG:
                raise
            context[self.var_name] = []
            return ''
        if self.posts_to_show is not None:
            try:
                posts_to_show = template.resolve_variable(self.posts_to_show,
                                                          context)
            except template.VariableDoesNotExist:
                if settings.DEBUG:
                    raise
        if self.cache_expires is not None:
            try:
                cache_expires = template.resolve_variable(self.cache_expires,
                                                          context)
            except template.VariableDoesNotExist:
                if settings.DEBUG:
                    raise
        context[self.var_name] = pull_feed(feed_url,
                                           posts_to_show,
                                           cache_expires)
        return ''

@register.tag
def get_feed(parser, token):
    """
    Pull a RSS or Atom feed into the context as the supplied variable.

    ::
        {% get_feed feed_url [posts_to_show] [cache_expires] as var %}
        {% get_feed "https://foo.net/timeline?max=5&format=rss" 5 60 as myfeed %}

    feed_url:      full url to the feed (required)
    posts_to_show: Number of posts to pull. <=0 for all
                   (default: settings.FEEDUTIL_NUM_POSTS or -1)
    cache_expired: Number of minuites for the cache. <=0 for no cache.
                   (default: settings.FEEDUTIL_CACHE_MIN or 30)
    var:           Name of variable to set the feed to in the current context


    Format of var:

    ::

        [ { 'title': "A title" , 'summary': "The summary",
            'url': "http://foo.net/a-title",
            'published': datetime(10, 20, 2007) },
          ... ]


    """
    args = token.split_contents()
    args.pop(0)
    if len(args) < 3 or len(args) > 5 or args[-2] != 'as':
        raise template.TemplateSyntaxError("Malformed arguments to get_feed tag.")
    nargs = [args[-1]] + args[:-2]
    return GetFeedNode(*nargs)
    return { 'posts': pull_feed(feed_url, posts_to_show, cache_expires) }
