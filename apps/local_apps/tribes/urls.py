from django.conf.urls.defaults import *

from tribes.models import Tribe
from wiki import models as wiki_models

from tribes.thing import TribeThing
# @@@ should qs really be here?
tt = TribeThing(Tribe.objects.filter(deleted=False))

wiki_args = {'group_slug_field': 'slug',
             'group_qs': Tribe.objects.filter(deleted=False)}


urlpatterns = \
    tt.urls(url_prefix='', name_prefix='tribe_thing') + \
    patterns('',
        url(r'^create/$', 'tribes.views.create', name="tribe_create"),
        url(r'^your_tribes/$', 'tribes.views.your_tribes', name="your_tribes"),
        url(r'^tribe/(\w+)/$', 'tribes.views.tribe', name="tribe_detail"),
        url(r'^tribe/(\w+)/delete/$', 'tribes.views.delete', name="tribe_delete"),
        
        # topics
        url(r'^tribe/(\w+)/topics/$', 'tribes.views.topics', name="tribe_topics"),
        url(r'^topic/(\d+)/edit/$', 'tribes.views.topic', kwargs={"edit": True}, name="tribe_topic_edit"),
        url(r'^topic/(\d+)/delete/$', 'tribes.views.topic_delete', name="tribe_topic_delete"),
        url(r'^topic/(\d+)/$', 'tribes.views.topic', name="tribe_topic"),
        
        # wiki
        url(r'^tribe/(?P<group_slug>\w+)/wiki/', include('wiki.urls'), kwargs=wiki_args),
    )