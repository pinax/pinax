from django.conf.urls.defaults import *

from pinax.apps.tribes.models import Tribe

from groups.bridge import ContentBridge



bridge = ContentBridge(Tribe)



urlpatterns = patterns("pinax.apps.tribes.views",
    url(r"^$", "tribes", name="tribe_list"),
    url(r"^create/$", "create", name="tribe_create"),
    url(r"^your_tribes/$", "your_tribes", name="your_tribes"),
    
    # tribe-specific
    url(r"^tribe/(?P<group_slug>[-\w]+)/$", "tribe", name="tribe_detail"),
    url(r"^tribe/(?P<group_slug>[-\w]+)/delete/$", "delete", name="tribe_delete"),
)


urlpatterns += bridge.include_urls("pinax.apps.topics.urls", r"^tribe/(?P<tribe_slug>[-\w]+)/topics/")
urlpatterns += bridge.include_urls("wakawaka.urls", r"^tribe/(?P<tribe_slug>[-\w]+)/wiki/")
urlpatterns += bridge.include_urls("pinax.apps.photos.urls", r"^tribe/(?P<tribe_slug>[-\w]+)/photos/")
