from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'profiles.views.profiles', name='profile_list'),
    url(r'^(?P<username>[\w]+)/$', 'profiles.views.profile', name='profile_detail'),
)
