from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^(\w+)/$', 'profiles.views.profile'),
)
