from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^personal/$', 'lifestream.views.personal'),
    (r'^friends/$', 'lifestream.views.friends'),
    (r'^(\w+)/$', 'lifestream.views.single'),
)
