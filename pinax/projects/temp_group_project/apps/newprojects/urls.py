from django.conf.urls.defaults import *

from newprojects.models import Project

from groups_ng.bridge import ContentBridge

include_kwargs = {
    'bridge': ContentBridge(Project, 'projects'),
}

urlpatterns = patterns('newprojects.views',
    url(r'^$', 'projects', name="project_list"), 
    url(r'^create/$', 'create', name="project_create"),
    url(r'^your_projects/$', 'your_projects', name="your_projects"),
    # project-specific
    url(r'^project/(?P<group_slug>[-\w]+)/$', 'project', name="project_detail"),
    url(r'^project/(?P<group_slug>[-\w]+)/delete/$', 'delete', name="project_delete"),
    url(r'^project/(?P<group_slug>[-\w]+)/topics/', include('topics.urls'), kwargs=include_kwargs),
)