from django.db.models import signals

from django.utils.translation import ugettext_noop as _

try:
    from notification import models as notification
    
    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("tribes_friend_joined", _("Friend Joined Tribe"), _("a friend of yours joined a tribe"), default=1)
        notification.create_notice_type("tribes_new_member", _("New Tribe Member"), _("a tribe you are a member of has a new member"), default=1)
        notification.create_notice_type("tribes_created_new_member", _("New Member Of Tribe You Created"), _("a tribe you created has a new member"), default=2)
        notification.create_notice_type("tribes_new_tribe", _("New Tribe Created"), _("a new tribe has been created"), default=1)
        notification.create_notice_type("tribes_friend_tribe", _("Friend Created Tribe"), _("a friend has created a new tribe"), default=1)
        
        notification.create_notice_type("tribes_new_topic", _("New Topic Started"), _("a new topic has started in a tribe you're a member of"), default=2)
        notification.create_notice_type("tribes_topic_response", _("Response To Your Topic"), _("someone has responded on a topic you started"), default=2)
    
    signals.post_syncdb.connect(create_notice_types, sender=notification)
except ImportError:
    print "Skipping creation of NoticeTypes as notification app not found"
