from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^login/$', 'bbauth.views.login', name="bbauth_login"),
    url(r'^success/$', 'bbauth.views.success', name="bbauth_success"),
    url(r'^logout/$', 'bbauth.views.logout', name="bbauth.logout"),
)