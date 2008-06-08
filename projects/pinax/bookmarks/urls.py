from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'bookmarks.views.bookmarks'),
    (r'^add/$', 'bookmarks.views.add'),
)
