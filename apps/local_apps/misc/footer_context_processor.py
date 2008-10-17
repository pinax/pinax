from zwitschern.models import Tweet
from tribes.models import Tribe
from django.contrib.auth.models import User
from bookmarks.models import Bookmark
from blog.models import Post

def footer(request):
    return {
        'latest_tweets': Tweet.objects.all().order_by('-sent')[:5],
        'latest_tribes': Tribe.objects.all().order_by('-created')[:5],
        'latest_users': User.objects.all().order_by('-date_joined')[:9],
        'latest_bookmarks': Bookmark.objects.all().order_by('-added')[:5],
        'latest_blogs': Post.objects.filter(status=2).order_by('-publish')[:5],
    }
