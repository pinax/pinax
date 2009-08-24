from django.conf.urls.defaults import *

from tribes.models import Tribe

from groups.bridge import ContentBridge


bridge = ContentBridge(Tribe, 'tribes')

urlpatterns = patterns('tribes.views',
    url(r'^$', 'tribes', name="tribe_list"),
    url(r'^create/$', 'create', name="tribe_create"),
    url(r'^your_tribes/$', 'your_tribes', name="your_tribes"),
    
    # tribe-specific
    url(r'^tribe/(?P<group_slug>[-\w]+)/$', 'tribe', name="tribe_detail"),
    url(r'^tribe/(?P<group_slug>[-\w]+)/delete/$', 'delete', name="tribe_delete"),
)

urlpatterns += bridge.include_urls('topics.urls', r'^tribe/(?P<group_slug>[-\w]+)/topics/')
urlpatterns += bridge.include_urls('wiki.urls', r'^tribe/(?P<group_slug>[-\w]+)/wiki/')
urlpatterns += bridge.include_urls('photos.urls', r'^tribe/(?P<group_slug>[-\w]+)/photos/')
