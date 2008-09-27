from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'zwitschern.views.personal', name='tweets_you_follow'),
    url(r'^all/$', 'zwitschern.views.public', name='all_tweets'),
    url(r'^(\d+)/$', 'zwitschern.views.single', name='single_tweet'),
)
