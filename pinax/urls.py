from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template
from django.contrib import admin

import os.path

from zwitschern.feeds import TweetFeedAll, TweetFeedUser, TweetFeedUserWithFriends
tweets_feed_dict = {"feed_dict": {
    'all': TweetFeedAll,
    'only': TweetFeedUser,
    'with_friends': TweetFeedUserWithFriends,
}}

from blog.feeds import BlogFeedAll, BlogFeedUser
blogs_feed_dict = {"feed_dict": {
    'all': BlogFeedAll,
    'only': BlogFeedUser,
}}

from bookmarks.feeds import BookmarkFeed
bookmarks_feed_dict = {"feed_dict": { '': BookmarkFeed }}

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', direct_to_template, {"template": "homepage.html"}, name="home"),
    url(r'^apps/$', direct_to_template, {"template": "apps.html"}, name="apps"),
    url(r'^sites/$', direct_to_template, {"template": "sites.html"}, name="sites"),
    url(r'^team/$', direct_to_template, {"template": "team.html"}, name="team"),
    
    (r'^about/', include('about.urls')),
    (r'^account/', include('account.urls')),
    (r'^openid/', include('account.openid_urls')),
    (r'^bbauth/', include('bbauth.urls')),
    (r'^authsub/', include('authsub.urls')),
    (r'^profiles/', include('profiles.urls')),
	(r'^blog/', include('blog.urls')),
	(r'^tags/', include('tag_app.urls')),
    (r'^invitations/', include('friends_app.urls')),
    (r'^notices/', include('notification.urls')),
    (r'^messages/', include('messages.urls')),
    (r'^announcements/', include('announcements.urls')),
    (r'^tweets/', include('zwitschern.urls')),
    (r'^lifestream/', include('lifestream.urls')),
    (r'^tribes/', include('tribes.urls')),
    (r'^projects/', include('projects.urls')),
    (r'^comments/', include('threadedcomments.urls')),
    (r'^robots.txt$', include('robots.urls')),
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^bookmarks/', include('bookmarks.urls')),
    (r'^admin/(.*)', admin.site.root),
    (r'^photos/', include('photos.urls')),
    #(r'^avatar/', include('avatar.urls')),
    (r'^games/', include('games.urls')),
    (r'^swaps/', include('swaps.urls')),
    (r'^locations/', include('locations.urls')),
    
    (r'^feeds/tweets/(.*)/$', 'django.contrib.syndication.views.feed', tweets_feed_dict),
    (r'^feeds/posts/(.*)/$', 'django.contrib.syndication.views.feed', blogs_feed_dict),
    (r'^feeds/bookmarks/(.*)/?$', 'django.contrib.syndication.views.feed', bookmarks_feed_dict),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': os.path.join(os.path.dirname(__file__), "site_media")}),
    )

