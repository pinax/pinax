from django.conf.urls.defaults import *

from newtribes.models import Tribe

from groups_ng.bridge import ContentBridge

include_kwargs = {
    'bridge': ContentBridge(Tribe, 'tribes'),
}

urlpatterns = patterns('newtribes.views',
    url(r'^$', 'tribes', name="tribe_list"), 
    url(r'^create/$', 'create', name="tribe_create"),
    url(r'^your_tribes/$', 'your_tribes', name="your_tribes"),
    # tribe-specific
    url(r'^tribe/(?P<group_slug>[-\w]+)/$', 'tribe', name="tribe_detail"),
    url(r'^tribe/(?P<group_slug>[-\w]+)/delete/$', 'delete', name="tribe_delete"),
    url(r'^tribe/(?P<group_slug>[-\w]+)/topics/', include('topics.urls'), kwargs=include_kwargs),
)