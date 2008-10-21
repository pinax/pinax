
from django.db.models import get_models, signals

try:
    from notification import models as notification
    
    def create_notice_types(app, created_models, verbosity, **kwargs):
        """
        Create the announcement notice type for sending notifications when
        announcements occur.
        """
        notification.create_notice_type("announcement", "Announcement", "you have received an announcement")
    
    signals.post_syncdb.connect(create_notice_types, sender=notification)
except ImportError:
    print "Skipping creation of NoticeTypes as notification app not found"
