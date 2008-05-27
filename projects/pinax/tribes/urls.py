from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'tribes.views.tribes'),
    (r'^(\w+)/$', 'tribes.views.tribe'),
)
