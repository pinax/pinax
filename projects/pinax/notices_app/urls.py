from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'notices_app.views.notices'),
)
