from django.conf.urls.defaults import *
from tasks.feeds import AllTaskFeed

tasks_feed_dict = {"feed_dict": {
    'all': AllTaskFeed,
}}

urlpatterns = patterns('',
        url(r'^$', 'tasks.views.tasks', name="task_list"),
        url(r'^(?P<field>modified|state|assignee|tag)/(?P<value>[^/]+)/$', 'tasks.views.focus', name="task_focus"),
        url(r'^add/$', 'tasks.views.add_task', name="task_add"),
        url(r'^add/with-paste/(?P<secret_id>\w+)/$', 'tasks.views.add_task', name="task_add_paste"),
        url(r'^task/(?P<id>\d+)/$', 'tasks.views.task', name="task_detail"),
        url(r'^tasks_for_user/(?P<username>[-\w]+)/$', 'tasks.views.user_tasks', name="tasks_for_user"),
        url(r'^mini_list/$', 'tasks.views.mini_list', name="tasks_mini_list"),

        # history
        url(r'^history/$', 'tasks.views.tasks_history_list', name="tasks_history_list"),
        url(r'^history/(?P<id>\d+)/$', 'tasks.views.tasks_history', name="tasks_history"),

        # nudge
        url(r'^nudge/(?P<id>\d+)/$', 'tasks.views.nudge', name="tasks_nudge"),

        # exports
        url(r'^export_state_transitions.csv$', 'tasks.views.export_state_transitions', name="tasks_export_state_transitions"),
        
        # feeds
        (r'^feeds/(.*)/$', 'django.contrib.syndication.views.feed', tasks_feed_dict),
    )
