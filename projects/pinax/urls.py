from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template

import os.path

from zwitschern.feeds import TweetFeed
feed_dict = {"feed_dict": {
    'tweets': TweetFeed,
}}

urlpatterns = patterns('',
    url(r'^$', direct_to_template, {"template": "homepage.html"}, name="home"),
    (r'^apps/$', direct_to_template, {"template": "apps.html"}),
    (r'^sites/$', direct_to_template, {"template": "sites.html"}),
    (r'^team/$', direct_to_template, {"template": "team.html"}),
    
    (r'^about/', include('about.urls')),
    (r'^account/', include('account.urls')),
    (r'^openid/', include('account.openid_urls')),
    (r'^bbauth/', include('bbauth.urls')),
    (r'^authsub/', include('authsub.urls')),
    (r'^profiles/', include('profiles.urls')),
    (r'^invitations/', include('friends_app.urls')),
    (r'^notices/', include('notification.urls')),
    (r'^messages/', include('messages.urls')),
    (r'^announcements/', include('announcements.urls')),
    (r'^tweets/', include('zwitschern.urls')),
    (r'^tribes/', include('tribes.urls')),
    (r'^comments/', include('threadedcomments.urls')),
    (r'^robots.txt$', include('robots.urls')),
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^bookmarks/', include('bookmarks.urls')),
    (r'^admin/', include('django.contrib.admin.urls')),
    
    (r'^feeds/(.*)/$', 'django.contrib.syndication.views.feed', feed_dict),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': os.path.join(os.path.dirname(__file__), "site_media")}),
    )

