from django.conf.urls.defaults import *

from basic_groups.models import BasicGroup

from groups.bridge import ContentBridge


bridge = ContentBridge(BasicGroup, 'basic_groups')


urlpatterns = patterns('',
    url(r'^create/$', 'basic_groups.views.create', name="group_create"),
    url(r'^your_groups/$', 'basic_groups.views.your_groups', name="your_groups"),
    
    url(r'^$', 'basic_groups.views.groups', name="group_list"),
    
    # group-specific
    url(r'^group/(?P<group_slug>[-\w]+)/$', 'basic_groups.views.group', name="group_detail"),
    url(r'^group/(?P<group_slug>[-\w]+)/delete/$', 'basic_groups.views.delete', name="group_delete"),
)


urlpatterns += bridge.include_urls('topics.urls', r'^group/(?P<group_slug>[-\w]+)/topics/')