from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'basic_profiles.views.profiles', name='profile_list'),
    url(r'^(?P<username>[\w]+)/$', 'basic_profiles.views.profile', name='profile_detail'),
    # url(r'^username_autocomplete/$', 'profiles.views.username_autocomplete', name='profile_username_autocomplete'),
)
