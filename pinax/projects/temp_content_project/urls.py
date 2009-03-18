from django.conf.urls.defaults import *
from django.conf import settings

from account.openid_consumer import PinaxConsumer

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^account/', include('account.urls')),
    (r'^openid/(.*)', PinaxConsumer()),
    (r'^profiles/', include('basic_profiles.urls')),
    (r'^notices/', include('notification.urls')),
    (r'^announcements/', include('announcements.urls')),
    (r'^admin/(.*)', admin.site.root),
    (r'', include('pages.urls')),
)

if settings.SERVE_MEDIA:
    urlpatterns += patterns('', 
        (r'^site_media/(?P<path>.*)$', 'misc.views.serve')
    )
