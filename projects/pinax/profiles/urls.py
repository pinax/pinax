from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'profiles.views.profiles'),
    (r'^(\w+)/$', 'profiles.views.profile'),
)
