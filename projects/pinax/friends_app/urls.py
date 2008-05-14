from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'friends_app.views.friends'),
)
