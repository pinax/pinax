from django.db.models import signals, get_app
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_noop as _

try:
    notification = get_app('notification')
    
    # @@@ when implemented need to add back "in a project you're a member of" or similar
    
    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("tasks_new", _("New Task"), _("a new task been created"), default=2)
        notification.create_notice_type("tasks_comment", _("Task Comment"), _("a new comment has been made on a task"), default=2)
        notification.create_notice_type("tasks_change", _("Task State Change"), _("there has been a change in the state of a task"), default=2)
        notification.create_notice_type("tasks_assignment", _("Task Assignment"), _("a task has been (re)assigned"), default=2)
        notification.create_notice_type("tasks_status", _("Task Status Update"), _("there has been a status update to a task"), default=2)
        notification.create_notice_type("tasks_tags", _("Task Tag Update"), _("there has been a change in the tagging of a task"), default=2)
        notification.create_notice_type("tasks_nudge", _("Task Nudge"), _("there has been a nudge of a task"), default=2)
        
    signals.post_syncdb.connect(create_notice_types, sender=notification)
except ImproperlyConfigured:
    print "Skipping creation of NoticeTypes as notification app not found"
