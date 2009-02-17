from django.conf.urls.defaults import *

from temp_projects.models import Project
from wiki import models as wiki_models

wiki_args = {
    'group_slug_field': 'slug',
    'group_qs': Project.objects.filter(deleted=False),
    'is_member': (lambda user, group: group.has_member(user)),
    'is_private': (lambda group: group.private),
}

urlpatterns = \
    patterns('',
        url(r'^create/$', 'temp_projects.views.create', name="project_create"),
        url(r'^your_projects/$', 'temp_projects.views.your_projects', name="your_projects"),
        
        url(r'^$', 'temp_projects.views.projects', name="project_list"),
        url(r'^order/topics/least-topics/$', 'temp_projects.views.projects',
            {'order': 'least_topics'}, name="project_list_least_topics"),
        url(r'^order/topics/most-topics/$', 'temp_projects.views.projects',
            {'order': 'most_topics'}, name="project_list_most_topics"),
        url(r'^order/members/least-members/$', 'temp_projects.views.projects',
            {'order': 'least_members'}, name="project_list_least_members"),
        url(r'^order/members/most-members/$', 'temp_projects.views.projects',
            {'order': 'most_members'}, name="project_list_most_members"),
        url(r'^order/name/ascending/$', 'temp_projects.views.projects',
            {'order': 'name_ascending'}, name="project_list_name_ascending"),
        url(r'^order/name/descending/$', 'temp_projects.views.projects',
            {'order': 'name_descending'}, name="project_list_name_descending"),
        url(r'^order/date/oldest/$', 'temp_projects.views.projects',
            {'order': 'date_oldest'}, name="project_list_date_oldest"),
        url(r'^order/date/newest/$', 'temp_projects.views.projects',
            {'order': 'date_newest'}, name="project_list_date_newest"),
        
        # project-specific
        url(r'^project/([-\w]+)/$', 'temp_projects.views.project', name="project_detail"),
        url(r'^project/([-\w]+)/delete/$', 'temp_projects.views.delete', name="project_delete"),
        url(r'^project/([-\w]+)/members_status/$', 'temp_projects.views.members_status', name="project_members_status"),
        
        # topics
        url(r'^project/([-\w]+)/topics/$', 'temp_projects.views.topics', name="project_topics"),
        url(r'^topic/(\d+)/$', 'temp_projects.views.topic', name="project_topic"),
        
        # tasks
        url(r'^project/([-\w]+)/tasks/$', 'temp_projects.views.tasks', name="project_tasks"),
        url(r'^task/(\d+)/$', 'temp_projects.views.task', name="project_task"),
        url(r'^tasks/([-\w]+)/$', 'temp_projects.views.user_tasks', name="project_user_tasks"),
        
        # wiki
        url(r'^project/(?P<group_slug>\w+)/wiki/', include('wiki.urls'), kwargs=wiki_args),
    )
