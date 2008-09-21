from django.conf.urls.defaults import *

from projects.models import Project
from wiki import models as wiki_models

from projects.thing import ProjectThing
pt = ProjectThing(Project)

wiki_args = {
    'group_slug_field': 'slug',
    'group_qs': Project.objects.all()
}


urlpatterns = pt.urls(url_prefix='', name_prefix='project_thing') + patterns('',
    url(r'^create/$', 'projects.views.create', name="project_create"),
    # @@@ what to do about clash with project with slug 'your_projects'?
    url(r'^your_projects/$', 'projects.views.your_projects', name="your_projects"),
    url(r'^project/(\w+)/$', 'projects.views.project', name="project_detail"),
    
    url(r'^project/(\w+)/members_status/$', 'projects.views.members_status', name="project_members_status"),
    
    # topics
    url(r'^project/(\w+)/topics/$', 'projects.views.topics', name="project_topics"),
    url(r'^topic/(\d+)/$', 'projects.views.topic', name="project_topic"),
    
    # tasks
    url(r'^project/(\w+)/tasks/$', 'projects.views.tasks', name="project_tasks"),
    url(r'^task/(\d+)/$', 'projects.views.task', name="project_task"),
    url(r'^tasks/(\w+)/$', 'projects.views.user_tasks', name="project_user_tasks"),
    
    # wiki
    url(r'^project/(?P<group_slug>\w+)/wiki/', include('wiki.urls'), kwargs=wiki_args),
)
