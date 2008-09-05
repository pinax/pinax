from django.conf import settings
from zwitschern.models import Tweet 
from tribes.models import Tribe 
from django.contrib.auth.models import User 
from bookmarks.models import Bookmark


def contact_email(request):
    return {'contact_email': getattr(settings, 'CONTACT_EMAIL', '')}

def site_name(request):
    return {'site_name': getattr(settings, 'SITE_NAME', '')}

def footer(request): 
 	return {
        'latest_tweets': Tweet.objects.all().order_by('-sent')[:5], 
        'latest_tribes': Tribe.objects.all().order_by('-created')[:5], 
        'latest_users': User.objects.all().order_by('-date_joined')[:5], 
        'latest_bookmarks': Bookmark.objects.all().order_by('-added')[:5],
    }

