from django.db.models import signals

from django.utils.translation import ugettext_noop as _

try:
    from notification import models as notification
    
    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("projects_new_member", _("New Project Member"), _("a project you are a member of has a new member"), default=1)
        notification.create_notice_type("projects_added_as_member", _("Added to Project"), _("you have been added to a project"), default=2)
        
        notification.create_notice_type("projects_deleted", _("Project Deleted"), _("a project you are a member of has been deleted"), default=2)
        
        notification.create_notice_type("projects_new_topic", _("New Project Topic Started"), _("a new topic has started in a project you're a member of"), default=2)
        notification.create_notice_type("projects_topic_response", _("Response To Your Project Topic"), _("someone has responded on a project topic you started"), default=2)
        
        notification.create_notice_type("projects_new_task", _("New Project Task"), _("a new task been created in a project you're a member of"), default=2)
        notification.create_notice_type("projects_task_comment", _("Comment on Project Task"), _("a new comment has been made on a task in a project you're a member of"), default=2)
        notification.create_notice_type("projects_task_change", _("Change to Project Task"), _("there has been a change in the state of a task in a project you're a member of"), default=2)
        notification.create_notice_type("projects_task_assignment", _("Change to Project Task"), _("a task has been (re)assigned in a project you're a member of"), default=2)
        notification.create_notice_type("projects_task_status", _("Change to Project Task"), _("there has been a status update to a task in a project you're a member of"), default=2)
        
    signals.post_syncdb.connect(create_notice_types, sender=notification)
except ImportError:
    print "Skipping creation of NoticeTypes as notification app not found"
