from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'topics.views.topics', name="topic_list"),
    url(r'^(?P<topic_id>\d+)/edit/$', 'topics.views.topic', kwargs={"edit": True}, name="topic_edit"),
    url(r'^(?P<topic_id>\d+)/delete/$', 'topics.views.topic_delete', name="topic_delete"),
    url(r'^(?P<topic_id>\d+)/$', 'topics.views.topic', name="topic_detail"),
)
