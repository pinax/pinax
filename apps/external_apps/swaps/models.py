from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from tagging.fields import TagField
from tagging.models import Tag

try:
    from notification import models as notification
    from django.db.models import signals
except ImportError:
    notification = None

class Offer(models.Model):
    
    """An offer to swap something between users
    
    An offer optionally includes what the offerer wants in exchange.
    
    Once an offer reaches the proposed state (proposes a swap), 
    it cannot be included in any other swaps.  However,
    an offer may be included as the responding offer 
    in many swaps.
    
    Once an offer reaches the swapped state,
    nothing can be changed except moving the state to fulfilled.
    The fulfilled state is optional.
    
    """
    
    STATE_CHOICES = (
        ('1', _('offered')),
        ('2', _('proposed')), # is the proposing offer of a proposed swap
        ('3', _('swapped')), # is included in an accepted swap
        ('4', _('fulfilled')), # the offering has been delivered
        ('5', _('canceled')), # the offer has been canceled
    )
    
    offerer = models.ForeignKey(User, verbose_name=_('offerer'))
    short_description = models.CharField(_('short description'), max_length=64)
    offering = models.TextField(_('offering'))
    want = models.TextField(_('want'), blank=True, null=True)
    state = models.CharField(_('state'), max_length="1", choices=STATE_CHOICES, default=1)
    offered_time = models.DateTimeField(_('offered time'), default=datetime.now)
    swapped_by = models.ForeignKey('Swap', blank=True, null=True, verbose_name=_('swapped by'))
    tags = TagField()
    
    def __unicode__(self):
        return self.short_description
    
    def get_absolute_url(self):
        return ('offer', [self.id])
    get_absolute_url = models.permalink(get_absolute_url)
    
    def is_changeable(self):
        
        """ If state is swapped, can only change state to fulfilled.
        
        If state is fulfilled, no changes allowed at all.
        
        """
        
        if int(self.state) > 2:
            return False
        else:
            return True
        
    def is_cancelable(self):
        answer = True
        if self.proposed_swaps.filter(state__lte=3):
            answer = False
        elif self.responding_swaps.filter(state__lte=3):
            answer = False
        return answer
    
    def cancel(self):
        if self.is_cancelable():
            self.state = 5
            self.save()
    
    def is_deletable(self):
        answer = True
        if self.proposed_swaps.all():
            answer = False
        elif self.responding_swaps.all():
            answer = False
        return answer
        
    def propose(self):
        if self.is_changeable():
            self.state = 2
            self.save()
            
    def swap(self, swap):
        """
        This method cannot save.
        Called from Swap, must be covered by Swap transaction.    
        """
        
        if self.is_changeable():
            self.state = 3
            self.swapped_by = swap
            #self.save()
            
    def fulfill(self):
        """ This method assumes that fulfillment starts at offers """
        if int(self.state) == 3:
            self.state = 4
            self.save()
            self.swapped_by.offer_fulfilled()
            
    def is_fulfilled(self):
        return self.state == 4
            
    def revert(self):
        """        
        This method cannot save.
        Called from Swap, must be covered by Swap transaction.            
        """
        
        if self.is_changeable():
            self.state = 1
            #self.save()
            
    def proposed_swap(self):
        if self.proposed_swaps:
            return self.proposed_swaps.all()[0]
        else:
            return None


class Swap(models.Model):
    
    """An exchange of anything between offers.
    
    When a swap is accepted, the state of both offers is changed to swapped.
    Any other swaps involving either of the accepted offers must be changed
    to the conflicted state.  In that state, the swap is effectively dead.
    
    If the swap is rejected or canceled, the state of both offers is changed
    back to offered.
    
    The fulfilled state is optional.
    
    Note:  at this stage, swaps can only include 2 offers.
    That may prove to be too restrictive, but it's simple.
    
    """
    
    STATE_CHOICES = (
        ('1', _('proposed')), # proposed by the proposing offer
        ('2', _('accepted')), # the responding offer has accepted the swap
        ('3', _('fulfilled')), # all offers have been delivered
        ('4', _('rejected')), # the responding offer has rejected the swap
        ('5', _('canceled')), # the proposing offer has canceled the swap
        ('6', _('conflicted')), # another swap took one of these offers
    )
    
    proposing_offer = models.ForeignKey(Offer, related_name='proposed_swaps', verbose_name=_('proposing offer'))
    responding_offer = models.ForeignKey(Offer, related_name='responding_swaps', verbose_name=_('responding offer'))
    state = models.CharField(_('state'), max_length="1", choices=STATE_CHOICES, default=1)
    proposed_time = models.DateTimeField(_('proposed time'), default=datetime.now)
    accepted_time = models.DateTimeField(_('accepted time'), blank=True, null=True)
    fulfilled_time = models.DateTimeField(_('fulfilled time'), blank=True, null=True)
    killed_time = models.DateTimeField(_('killed time'), blank=True, null=True)
    conflicted_by = models.ForeignKey('self', blank=True, null=True, related_name='conflicting_swap', verbose_name=_('conflicted by'))
    
    def __unicode__(self):
        return _('Proposing offer: %s, Responding offer %s') % (
            self.proposing_offer.short_description,
            self.responding_offer.short_description
        )
        
    def get_absolute_url(self):
        return ('swap', [self.id])
    get_absolute_url = models.permalink(get_absolute_url)

        
    def swap_offers(self):
        self.proposing_offer.swap(self)
        self.responding_offer.swap(self)
        
    def revert_offers(self):
        self.proposing_offer.revert()
        self.responding_offer.revert()
        
    def accept(self):
        self.state = 2
        self.swap_offers()
        self.accepted_time = datetime.now()
        
    def fulfill(self):
        self.state = 3
        self.fulfilled_time = datetime.now()
        self.save()
        
    def offer_fulfilled(self):
        if self.proposing_offer.is_fulfilled() and self.responding_offer.is_fulfilled():
            self.fulfill()
           
    def reject(self):
        self.state = 4
        self.killed_time = datetime.now()
        self.revert_offers()
        
    def cancel(self):
        self.state = 5
        self.killed_time = datetime.now()
        self.revert_offers()
        
    def conflict(self, conflicting_swap):
        self.state = 6
        self.conflicted_by = conflicting_swap
        self.killed_time = datetime.now()
        self.revert_offers()
        if notification:
            notification.send([self.proposing_offer.offerer,], "swaps_conflict", 
                {"losing_swap": self, 
                 "winning_swap": conflicting_swap})
            notification.send([self.responding_offer.offerer,], "swaps_conflict", 
                {"losing_swap": self, 
                 "winning_swap": conflicting_swap})
              
    @transaction.commit_manually
    def save(self, force_insert=False, force_update=False):
        
        """ Enforce state change rules...
        
        and watch out for conflicting swaps.
        First swap to get to accepted state wins,
        all competing swaps' states set to conflicted.
        This swap might be the winner or the loser.
        
        """

        try:
            changeable = False 
            
            if self.pk:
                previous_state = Swap.objects.get(pk=self.pk).state
                if self.state != previous_state:
                    if int(self.state) == 6:
                        changeable = True
                    elif int(previous_state) == 1:
                        changeable = True
                        if int(self.state) == 2:
                            competing_swaps = list(self.proposing_offer.proposed_swaps.all())
                            competing_swaps.extend(list(self.proposing_offer.responding_swaps.all()))
                            competing_swaps.extend(list(self.responding_offer.proposed_swaps.all()))
                            competing_swaps.extend(list(self.responding_offer.responding_swaps.all()))
                            for swap in competing_swaps:
                                if swap.pk != self.pk:
                                    if swap.state == 2: # this swap loses a conflict
                                        self.conflict(swap)
            else:
                changeable = True
                
            if changeable: 
                super(Swap, self).save(force_insert, force_update)
                # swap offers usually changed when swap changes
                # must be covered in same transaction
                self.proposing_offer.save()
                self.responding_offer.save()
                if int(self.state) == 1:
                    self.proposing_offer.propose()
                elif int(self.state) == 2:
                    for swap in competing_swaps: # this swap wins any conflicts
                        if swap.pk != self.pk:
                            swap.conflict(self)
                            swap.save()
        except:
            transaction.rollback()
        else:
            transaction.commit()

# handle notification of new comments
from threadedcomments.models import ThreadedComment
def new_comment(sender, instance, **kwargs):
    if isinstance(instance.content_object, Swap):
        swap = instance.content_object
        if notification:
            commenter = instance.user
            recipient = swap.responding_offer.offerer
            if commenter.id == recipient.id:
                recipient = swap.proposing_offer.offerer
            notification.send([recipient], "swaps_comment", 
                {"commenter": commenter, "swap": swap, "comment": instance})
signals.post_save.connect(new_comment, sender=ThreadedComment)