from django.conf.urls.defaults import *

urlpatterns = patterns('',
    #url(r'^username_autocomplete/$', 'autocomplete_app.views.username_autocomplete_friends', name='profile_username_autocomplete'),
    url(r'^username_autocomplete/$', 'autocomplete_app.views.username_autocomplete_all', name='profile_username_autocomplete'),
    url(r'^$', 'basic_profiles.views.profiles', name='profile_list'),
    url(r'^(?P<username>[\w\._-]+)/$', 'basic_profiles.views.profile', name='profile_detail'),
)
