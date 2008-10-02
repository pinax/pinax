from django.conf import settings
from zwitschern.models import Tweet 
from tribes.models import Tribe 
from django.contrib.auth.models import User 
from bookmarks.models import Bookmark
from blog.models import Post
from core.utils import inbox_count_sources

def contact_email(request):
    return {'contact_email': getattr(settings, 'CONTACT_EMAIL', '')}

def site_name(request):
    return {'site_name': getattr(settings, 'SITE_NAME', '')}

def footer(request): 
    return {
        'latest_tweets': Tweet.objects.all().order_by('-sent')[:5], 
        'latest_tribes': Tribe.objects.all().order_by('-created')[:5], 
        'latest_users': User.objects.all().order_by('-date_joined')[:9], 
        'latest_bookmarks': Bookmark.objects.all().order_by('-added')[:5],
        'latest_blogs': Post.objects.filter(status=2).order_by('-publish')[:5],
    }

def combined_inbox_count(request):
    """
    A context processor that uses other context processors defined in
    setting.COMBINED_INBOX_COUNT_SOURCES to return the combined number from
    arbitrary counter sources.
    """
    count = 0
    for func in inbox_count_sources():
        counts = func(request)
        if counts:
            for value in counts.itervalues():
                try:
                    count = count + int(value)
                except (TypeError, ValueError):
                    pass
    return {'combined_inbox_count': count,}
