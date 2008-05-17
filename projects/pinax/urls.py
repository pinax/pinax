from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template

import os.path

urlpatterns = patterns('',
    (r'^$', direct_to_template, {"template": "homepage.html"}),
    
    (r'^about/', include('about.urls')),
    (r'^account/', include('account.urls')),
    (r'^profiles/', include('profiles.urls')),
    (r'^friends/', include('friends_app.urls')),
    (r'^notices/', include('notices_app.urls')),
    
    (r'^robots.txt$', include('robots.urls')),
    (r'^admin/', include('django.contrib.admin.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': os.path.join(os.path.dirname(__file__), "site_media")}),
    )

