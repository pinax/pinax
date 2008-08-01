from django.conf.urls.defaults import *

from tribes.models import Tribe
from wiki import models as wiki_models


wiki_args = {'group_slug_field': 'slug',
             'group_qs': Tribe.objects.all()}


urlpatterns = patterns('',
    url(r'^$', 'tribes.views.tribes', name="tribes_list"),
    url(r'^your_tribes/$', 'tribes.views.your_tribes', name="your_tribes"),
    url(r'^(\w+)/$', 'tribes.views.tribe', name="tribe_detail"),

    # topics
    url(r'^(\w+)/topics/$', 'tribes.views.topics', name="tribe_topics"),
    url(r'^topic/(\d+)/edit/$', 'tribes.views.topic', kwargs={"edit": True}, name="tribe_topic_edit"),
    url(r'^topic/(\d+)/delete/$', 'tribes.views.topic_delete', name="tribe_topic_delete"),
    url(r'^topic/(\d+)/$', 'tribes.views.topic', name="tribe_topic"),

    # wiki
    url(r'^(?P<group_slug>\w+)/wiki/', include('wiki.urls'),
        kwargs=wiki_args),
)
