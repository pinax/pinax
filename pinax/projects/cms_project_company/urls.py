from django.conf.urls.defaults import *
from django.conf import settings

from django.views.generic.simple import direct_to_template

from account.openid_consumer import PinaxConsumer

from django.contrib import admin
admin.autodiscover()

import os

urlpatterns = patterns('',
    # some simple pages
    url(r'^$', direct_to_template, {"template": "homepage.html"}, name="home"),
    url(r'^products/$', direct_to_template, {"template": "products.html"}, name="products"),
    url(r'^support/$', direct_to_template, {"template": "support.html"}, name="support"),
    url(r'^about_us/$', direct_to_template, {"template": "about_us.html"}, name="about_us"),
    
    # 3rd party
    (r'^frontendadmin/', include('frontendadmin.urls')),
    (r'^attachments/', include('attachments.urls')),
    
    # pinax provided
    (r'^account/', include('account.urls')),
    (r'^openid/(.*)', PinaxConsumer()),
    (r'^admin/(.*)', admin.site.root),
)

if settings.SERVE_MEDIA:
    urlpatterns += patterns('',
        (r'^site_media/', include('staticfiles.urls')),
    )
