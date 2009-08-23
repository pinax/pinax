from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('', 
    (r'^static/(?P<path>.*)$', 'staticfiles.views.serve'),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT
    }),
)
