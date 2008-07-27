from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'zwitschern.views.personal'),
    (r'^all/$', 'zwitschern.views.public'),
    (r'^(\d+)/$', 'zwitschern.views.single'),
)
