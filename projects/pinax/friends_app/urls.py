from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'friends_app.views.friends'),
    (r'^accept/(\w+)/$', 'friends_app.views.accept_join'),
)
