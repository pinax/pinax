from django.db.models import signals

from django.utils.translation import ugettext_noop as _

try:
    from notification import models as notification
    
    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("blog_friend_post", _("Friend Posted to Blog"), _("a friend of yours posted to their blog"), default=2)
        notification.create_notice_type("blog_post_comment", _("New Comment on Blog Post"), _("a comment was made on one of your blog posts"), default=2)
    
    signals.post_syncdb.connect(create_notice_types, sender=notification)
except ImportError:
    print "Skipping creation of NoticeTypes as notification app not found"
