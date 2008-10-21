from django.conf.urls.defaults import *

# for voting
from voting.views import vote_on_object
from bookmarks.models import Bookmark

urlpatterns = patterns('',
    url(r'^$', 'bookmarks.views.bookmarks', name="all_bookmarks"),
    url(r'^your_bookmarks/$', 'bookmarks.views.your_bookmarks', name="your_bookmarks"),
    url(r'^add/$', 'bookmarks.views.add', name="add_bookmark"),
    url(r'^(\d+)/delete/$', 'bookmarks.views.delete', name="delete_bookmark_instance"),
    
    # for voting
    (r'^(?P<object_id>\d+)/(?P<direction>up|down|clear)vote/?$',
        vote_on_object, dict(
            model=Bookmark,
            template_object_name='bookmark',
            template_name='kb/link_confirm_vote.html',
            allow_xmlhttprequest=True)),
)
