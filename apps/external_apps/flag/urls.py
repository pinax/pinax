from django.conf.urls.defaults import *

urlpatterns = patterns('',    
    url(r'^$', 'flag.views.flag', name="flag"),
)