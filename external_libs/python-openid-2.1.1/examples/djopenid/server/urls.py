
from django.conf.urls.defaults import *

urlpatterns = patterns(
    'djopenid.server.views',
    (r'^$', 'server'),
    (r'^xrds/$', 'idpXrds'),
    (r'^processTrustResult/$', 'processTrustResult'),
    (r'^user/$', 'idPage'),
    (r'^endpoint/$', 'endpoint'),
    (r'^trust/$', 'trustPage'),
)
