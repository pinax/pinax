from django.conf.urls.defaults import *

from atom import Feed

urlpatterns = patterns('',
    (r'^$', 'notices_app.views.notices'),
)
