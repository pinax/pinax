from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^login/$', 'authsub.views.login'),
)