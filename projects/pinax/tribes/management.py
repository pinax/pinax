from django.dispatch import dispatcher
from django.db.models import signals

from django.utils.translation import ugettext_noop as _

try:
    from notification import models as notification
    
    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("tribes_friend_joined", _("Friend Joined Tribe"), _("a friend of yours joined a tribe"), default=1)
        notification.create_notice_type("tribes_new_member", _("New Tribe Member"), _("a tribe you are a member of has a new member"), default=1)
        notification.create_notice_type("tribes_new_tribe", _("New Tribe Created"), _("a new tribe has been created"), default=1)
        notification.create_notice_type("tribes_friend_tribe", _("Friend Created Tribe"), _("a friend has created a new tribe"), default=1)
    
    dispatcher.connect(create_notice_types, signal=signals.post_syncdb, sender=notification)
except ImportError:
    print "Skipping creation of NoticeTypes as notification app not found"
