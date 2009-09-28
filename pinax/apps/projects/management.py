from django.conf import settings
from django.db.models import signals
from django.utils.translation import ugettext_noop as _

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
    
    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("projects_new_member", _("New Project Member"), _("a project you are a member of has a new member"), default=1)
        notification.create_notice_type("projects_created_new_member", _("New Member Of Project You Created"), _("a project you created has a new member"), default=2)
        notification.create_notice_type("projects_new_project", _("New Project Created"), _("a new project has been created"), default=1)
        notification.create_notice_type("projects_added_as_member", _("Added as a Project Member"), _("you have become member of a project"), default=1)
        
    signals.post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Skipping creation of NoticeTypes as notification app not found"
