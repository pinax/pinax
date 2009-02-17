from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'topics.views.topics', name="tribe_topics"),
    url(r'^(\d+)/edit/$', 'topics.views.topic', kwargs={"edit": True}, name="tribe_topic_edit"),
    url(r'^(\d+)/delete/$', 'topics.views.topic_delete', name="tribe_topic_delete"),
    url(r'^(\d+)/$', 'topics.views.topic', name="tribe_topic"),
)
