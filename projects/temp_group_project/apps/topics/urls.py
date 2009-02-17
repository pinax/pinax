from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'topics.views.topics', name="topic_list"),
    url(r'^(\d+)/edit/$', 'topics.views.topic', kwargs={"edit": True}, name="topic_edit"),
    url(r'^(\d+)/delete/$', 'topics.views.topic_delete', name="topic_delete"),
    url(r'^(\d+)/$', 'topics.views.topic', name="topic_detail"),
)
