from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'zwitschern.views.personal', name='tweets_you_follow'),
    url(r'^all/$', 'zwitschern.views.public', name='all_tweets'),
    url(r'^(\d+)/$', 'zwitschern.views.single', name='single_tweet'),

    url(r'^followers/(\w+)/$', 'zwitschern.views.followers', name='tweet_followers'),
    url(r'^following/(\w+)/$', 'zwitschern.views.following', name='tweet_following'),
)
