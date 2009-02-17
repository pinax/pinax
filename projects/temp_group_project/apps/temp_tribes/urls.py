from django.conf.urls.defaults import *

from temp_tribes.models import Tribe


def get_tribe(request, slug):
    return Tribe.objects.get(slug=slug, deleted=False)


def user_is_member(request, group):
    if request.user.is_authenticated():
        return (request.user in group.members.all())
    else:
        return False


def new_topic_callback(request, topic):
    pass # @@@ notification.send(tribe.members.all(), "tribes_new_topic", {"topic": topic})


urlpatterns = patterns('',
    url(r'^create/$', 'temp_tribes.views.create', name="tribe_create"),
    url(r'^your_tribes/$', 'temp_tribes.views.your_tribes', name="your_tribes"),
    
    url(r'^$', 'temp_tribes.views.tribes', name="tribe_list"),
    url(r'^order/topics/least-topics/$', 'temp_tribes.views.tribes',
        {'order': 'least_topics'}, name="tribe_list_least_topics"),
    url(r'^order/topics/most-topics/$', 'temp_tribes.views.tribes',
        {'order': 'most_topics'}, name="tribe_list_most_topics"),
    url(r'^order/members/least-members/$', 'temp_tribes.views.tribes',
        {'order': 'least_members'}, name="tribe_list_least_members"),
    url(r'^order/members/most-members/$', 'temp_tribes.views.tribes',
        {'order': 'most_members'}, name="tribe_list_most_members"),
    url(r'^order/name/ascending/$', 'temp_tribes.views.tribes',
        {'order': 'name_ascending'}, name="tribe_list_name_ascending"),
    url(r'^order/name/descending/$', 'temp_tribes.views.tribes',
        {'order': 'name_descending'}, name="tribe_list_name_descending"),
    url(r'^order/date/oldest/$', 'temp_tribes.views.tribes',
        {'order': 'date_oldest'}, name="tribe_list_date_oldest"),
    url(r'^order/date/newest/$', 'temp_tribes.views.tribes',
        {'order': 'date_newest'}, name="tribe_list_date_newest"),
    
    # tribe-specific
    url(r'^tribe/([-\w]+)/$', 'temp_tribes.views.tribe', name="tribe_detail"),
    url(r'^tribe/([-\w]+)/delete/$', 'temp_tribes.views.delete', name="tribe_delete"),
    
    # topics
    url(r'^tribe/(?P<group_slug>\w+)/topics/', include('topics.urls'), kwargs={
        "get_group": get_tribe,
        "user_is_member": user_is_member,
        "new_topic_callback": new_topic_callback,
    }),
    
    # wiki
    url(r'^tribe/(?P<group_slug>\w+)/wiki/', include('wiki.urls'), kwargs={
        'group_slug_field': 'slug',
        'group_qs': Tribe.objects.filter(deleted=False)
    }),
)