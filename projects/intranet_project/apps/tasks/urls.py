from django.conf.urls.defaults import *

urlpatterns = patterns('',
        url(r'^$', 'tasks.views.tasks', name="task_list"),
        url(r'^(modified|state|assignee|tag)/([^/]+)/$', 'tasks.views.focus', name="task_focus"),
        url(r'^add/$', 'tasks.views.add_task', name="task_add"),
        url(r'^task/(\d+)/$', 'tasks.views.task', name="task_detail"),
        url(r'^tasks_for_user/([-\w]+)/$', 'tasks.views.user_tasks', name="tasks_for_user"),
        url(r'^mini_list/$', 'tasks.views.mini_list', name="tasks_mini_list"),
    )
