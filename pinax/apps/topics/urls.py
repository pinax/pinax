from django.conf.urls.defaults import *



urlpatterns = patterns("",
    url(r"^$", "pinax.apps.topics.views.topics", name="topic_list"),
    url(r"^(?P<topic_id>\d+)/edit/$", "pinax.apps.topics.views.topic", kwargs={"edit": True}, name="topic_edit"),
    url(r"^(?P<topic_id>\d+)/delete/$", "pinax.apps.topics.views.topic_delete", name="topic_delete"),
    url(r"^(?P<topic_id>\d+)/$", "pinax.apps.topics.views.topic", name="topic_detail"),
)
