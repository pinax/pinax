from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^username_autocomplete/$', 'misc.views.username_autocomplete_friends', name='profile_username_autocomplete'),
    url(r'^$', 'profiles.views.profiles', name='profile_list'),
    url(r'^(?P<username>[\w\._-]+)/$', 'profiles.views.profile', name='profile_detail'),
)
