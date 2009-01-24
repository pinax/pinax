from django.conf.urls.defaults import *
from django.conf import settings

from django.views.generic.simple import direct_to_template

from intranet_account.openid_consumer import PinaxConsumer

from django.contrib import admin
admin.autodiscover()

import os

from wiki import models as wiki_models

urlpatterns = patterns('',
    url(r'^$', direct_to_template, {"template": "homepage.html"}, name="home"),
    
    (r'^about/', include('about.urls')),
    (r'^account/', include('intranet_account.urls')),
    (r'^openid/(.*)', PinaxConsumer()),
    (r'^profiles/', include('basic_profiles.urls')),
    (r'^notices/', include('notification.urls')),
    (r'^announcements/', include('announcements.urls')),
    #(r'^pastebin/', include('pastebin.urls')),
    #(r'^quickbar/', include('quickbar.urls')),
    #(r'^documents/', include('documents.urls')),
    (r'^bookmarks/', include('bookmarks.urls')),
    (r'^tasks/', include('tasks.urls')),
    (r'^comments/', include('threadedcomments.urls')),
    (r'^wiki/', include('wiki.urls')),
    
    (r'^admin/(.*)', admin.site.root),
)

if settings.SERVE_MEDIA:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': os.path.join(os.path.dirname(__file__), "site_media")}),
    )
