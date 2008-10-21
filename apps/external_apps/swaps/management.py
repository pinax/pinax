from django.dispatch import dispatcher
from django.db.models import signals

from django.utils.translation import ugettext_noop as _

try:
    from notification import models as notification
    
    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("swaps_proposal", _("New Swap Proposal"), _("someone has proposed a swap for one of your offers"), default=2)
        notification.create_notice_type("swaps_acceptance", _("Swap Acceptance"), _("someone has accepted a swap that you proposed"), default=2)
        notification.create_notice_type("swaps_rejection", _("Swap Rejection"), _("someone has rejected a swap that you proposed"), default=2)
        notification.create_notice_type("swaps_cancellation", _("Swap Cancellation"), _("someone has canceled a proposed swap for one of your offers"), default=2)
        notification.create_notice_type("swaps_proposing_offer_changed", _("Swap Proposing Offer Changed"), _("someone has changed their proposing offer in a swap for one of your offers"), default=2)
        notification.create_notice_type("swaps_responding_offer_changed", _("Swap Responding Offer Changed"), _("someone has changed their responding offer in a swap that you proposed"), default=2)
        notification.create_notice_type("swaps_comment", _("Swap Comment"), _("someone has commented on a swap in which your offer is involved"), default=2)
        notification.create_notice_type("swaps_conflict", _("Swap Conflict"), _("your swap has lost a conflict to another swap"), default=2)

    signals.post_syncdb.connect(create_notice_types, sender=notification) 
except ImportError:
    print "Skipping creation of NoticeTypes as notification app not found"