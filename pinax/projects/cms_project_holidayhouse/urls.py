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
    url(r'^rooms/$', direct_to_template, {"template": "rooms.html"}, name="rooms"),
    url(r'^prices/$', direct_to_template, {"template": "prices.html"}, name="prices"),
    url(r'^contact/$', direct_to_template, {"template": "contact.html"}, name="contact"),
    
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
