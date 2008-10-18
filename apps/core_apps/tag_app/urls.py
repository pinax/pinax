from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # all tags
    url(r'^(?P<tag>.+)/$', 'tag_app.views.tags', name='tag_results'),
)
