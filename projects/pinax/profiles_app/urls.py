from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'profiles_app.views.profiles'),
    (r'^(\w+)/$', 'profiles_app.views.profile'),
)
