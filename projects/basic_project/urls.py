from django.conf.urls.defaults import *
from django.conf import settings

from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

import os

urlpatterns = patterns('',
    url(r'^$', direct_to_template, {"template": "homepage.html"}, name="home"),
    
    (r'^about/', include('about.urls')),
    (r'^account/', include('account.urls')),
    (r'^openid/', include('account.openid_urls')),
#    (r'^bbauth/', include('bbauth.urls')),
#    (r'^authsub/', include('authsub.urls')),
    (r'^profiles/', include('basic_profiles.urls')),
#    (r'^invitations/', include('friends_app.urls')),
#    (r'^notices/', include('notification.urls')),
#    (r'^messages/', include('messages.urls')),
#    (r'^announcements/', include('announcements.urls')),
#    (r'^robots.txt$', include('robots.urls')),
#    (r'^avatar/', include('avatar.urls')),
    
    (r'^admin/(.*)', admin.site.root),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': os.path.join(os.path.dirname(__file__), "site_media")}),
    )
