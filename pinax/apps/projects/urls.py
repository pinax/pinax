from django.conf.urls.defaults import *

from projects.models import Project

from groups.bridge import ContentBridge


bridge = ContentBridge(Project, 'projects')

urlpatterns = patterns('projects.views',
    url(r'^$', 'projects', name="project_list"),
    url(r'^create/$', 'create', name="project_create"),
    url(r'^your_projects/$', 'your_projects', name="your_projects"),
    # project-specific
    url(r'^project/(?P<group_slug>[-\w]+)/$', 'project', name="project_detail"),
    url(r'^project/(?P<group_slug>[-\w]+)/delete/$', 'delete', name="project_delete"),
)

urlpatterns += bridge.include_urls('topics.urls', r'^project/(?P<group_slug>[-\w]+)/topics/')
urlpatterns += bridge.include_urls('tasks.urls', r'^project/(?P<group_slug>[-\w]+)/tasks/')
urlpatterns += bridge.include_urls('wiki.urls', r'^project/(?P<group_slug>[-\w]+)/wiki/')
