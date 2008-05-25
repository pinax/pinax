from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template

import os.path

urlpatterns = patterns('',
    (r'^$', direct_to_template, {"template": "homepage.html"}),
    (r'^tab2/$', direct_to_template, {"template": "tabs.html"}),
    (r'^tab3/$', direct_to_template, {"template": "tabs.html"}),
    
    (r'^about/', include('about.urls')),
    (r'^account/', include('account.urls')),
    (r'^openid/', include('openid_urls')),
    (r'^profiles/', include('profiles.urls')),
    (r'^invitations/', include('friends_app.urls')),
    (r'^notices/', include('notification.urls')),
    (r'^messages/', include('messages.urls')),
    (r'^announcements/', include('announcements.urls')),
    (r'^tweets/', include('zwitschern.urls')),
    
    (r'^robots.txt$', include('robots.urls')),
    (r'^admin/', include('django.contrib.admin.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': os.path.join(os.path.dirname(__file__), "site_media")}),
    )

