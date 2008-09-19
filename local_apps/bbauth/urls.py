from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^login/$', 'bbauth.views.login'),
    url(r'^success/$', 'bbauth.views.success'),
    url(r'^logout/$', 'bbauth.views.logout'),
)