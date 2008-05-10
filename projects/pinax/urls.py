from django.conf.urls.defaults import *
from django.conf import settings

import os.path

urlpatterns = patterns('',
    (r'^$', 'core.views.homepage'),
    
    (r'^account/', include('account.urls')),
    
    (r'^admin/', include('django.contrib.admin.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': os.path.join(os.path.dirname(__file__), "site_media")}),
    )

