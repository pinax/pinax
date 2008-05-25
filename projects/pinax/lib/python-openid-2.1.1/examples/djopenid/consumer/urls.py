
from django.conf.urls.defaults import *

urlpatterns = patterns(
    'djopenid.consumer.views',
    (r'^$', 'startOpenID'),
    (r'^finish/$', 'finishOpenID'),
    (r'^xrds/$', 'rpXRDS'),
)
