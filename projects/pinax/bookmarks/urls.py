from django.conf.urls.defaults import *

# for voting
from voting.views import vote_on_object
from bookmarks.models import Bookmark

urlpatterns = patterns('',
    (r'^$', 'bookmarks.views.bookmarks'),
    (r'^add/$', 'bookmarks.views.add'),
    
    # for voting
    (r'^(?P<object_id>\d+)/(?P<direction>up|down|clear)vote/?$',
        vote_on_object, dict(
            model=Bookmark,
            template_object_name='bookmark',
            template_name='kb/link_confirm_vote.html',
            allow_xmlhttprequest=True)),
)
