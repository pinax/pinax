from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    (r'^$', direct_to_template, {"template": "about/about.html"}),
    
    (r'^terms/$', direct_to_template, {"template": "about/terms.html"}),
    (r'^privacy/$', direct_to_template, {"template": "about/privacy.html"}),
)
