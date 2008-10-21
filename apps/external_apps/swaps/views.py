from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic import date_based
from django.conf import settings
from django.db.models import Q

from swaps.models import Offer, Swap
from swaps.forms import OfferForm, ProposeSwapForm, ProposingOfferForm

try:
    from notification import models as notification
except ImportError:
    notification = None
    
try:
    from threadedcomments.models import ThreadedComment
    forums = True
except ImportError:
    forums = False

@login_required
def offers(request, username=None):
    offers = Offer.objects.filter(state=1).order_by("-offered_time")
    return render_to_response("swaps/offers.html", {"offers": offers}, context_instance=RequestContext(request))

@login_required
def offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    #deletable = offer.is_deletable()
    return render_to_response("swaps/offer.html", {
        "offer": offer,
        #"deletable": deletable,
    }, context_instance=RequestContext(request))

@login_required
def your_offers(request):
    user = request.user
    offers = Offer.objects.filter(offerer=user).order_by("-offered_time")
    return render_to_response("swaps/your_offers.html", {"offers": offers}, context_instance=RequestContext(request))

@login_required
def swap(request, swap_id):
    swap = get_object_or_404(Swap, id=swap_id)   
    return render_to_response("swaps/swap.html", {
        "swap": swap,
    }, context_instance=RequestContext(request))

@login_required
def proposed_by_you(request):
    swaps = Swap.objects.filter(proposing_offer__offerer=request.user, state=1).order_by("-proposed_time")
    return render_to_response("swaps/proposed_by_you.html", {"swaps": swaps}, context_instance=RequestContext(request))

@login_required
def proposed_to_you(request):
    swaps = Swap.objects.filter(responding_offer__offerer=request.user, state=1).order_by("-proposed_time")   
    return render_to_response("swaps/proposed_to_you.html", {"swaps": swaps}, context_instance=RequestContext(request))

@login_required
def accepted_swaps(request):
    swaps = Swap.objects.filter(
        Q(state=2, proposing_offer__offerer=request.user) |
        Q(state=2, responding_offer__offerer=request.user)).order_by("-accepted_time") 
    return render_to_response("swaps/accepted.html", {"swaps": swaps}, context_instance=RequestContext(request))

@login_required
def dead_swaps(request):
    swaps = Swap.objects.filter(
        Q(state__gt=3, proposing_offer__offerer=request.user) |
        Q(state__gt=3, responding_offer__offerer=request.user)).order_by("-killed_time") 
    return render_to_response("swaps/dead.html", {"swaps": swaps}, context_instance=RequestContext(request))


@login_required
def new(request):
    if request.method == "POST":
        if request.POST["action"] == "create":
            offer_form = OfferForm(request.POST)
            if offer_form.is_valid():
                offer = offer_form.save(commit=False)
                offer.offerer = request.user
                offer.save()
                request.user.message_set.create(message=_("Successfully saved offer '%s'") % offer.short_description)
               #if notification:
               #     if friends: # @@@ might be worth having a shortcut for sending to all friends
               #         notification.send((x['friend'] for x in Friendship.objects.friends_for_user(offer.offerer)), "offer_friend_post", {"post": blog})
                
                return HttpResponseRedirect(reverse("offer_list_yours"))
        else:
            offer_form = OfferForm()
    else:
        offer_form = OfferForm()
    
    return render_to_response("swaps/new_offer.html", {
        "offer_form": offer_form
    }, context_instance=RequestContext(request))
    
    
@login_required
def edit_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    if offer.offerer != request.user:
        request.user.message_set.create(message="You cannot edit offers that are not yours")
        return HttpResponseRedirect(reverse("offer_list_yours"))
    return_to = request.GET['returnto']
    if request.method == "POST":
        if request.POST["action"] == "update":
            offer_form = OfferForm(request.POST, instance=offer)
            if offer_form.is_valid():
                offer = offer_form.save(commit=False)
                offer.save()
                if notification:
                    for swap in offer.proposed_swaps.filter(state=1):
                        notification.send([swap.responding_offer.offerer,], "swaps_proposing_offer_changed", 
                            {"creator": request.user, 
                             "swap": swap, 
                             "proposing_offer": swap.proposing_offer, 
                             "responding_offer": swap.responding_offer})
                    for swap in offer.responding_swaps.filter(state=1):
                        notification.send([swap.proposing_offer.offerer,], "swaps_responding_offer_changed", 
                            {"creator": request.user, 
                             "swap": swap, 
                             "proposing_offer": swap.proposing_offer, 
                             "responding_offer": swap.responding_offer}) 
                    
                request.user.message_set.create(message=_("Successfully updated offer '%s'") % offer.short_description)
                return HttpResponseRedirect(reverse(return_to))
        else:
            offer_form = OfferForm(instance=offer)
    else:
        offer_form = OfferForm(instance=offer)
    
    return render_to_response("swaps/edit_offer.html", {
        "offer_form": offer_form,
        "offer": offer,
    }, context_instance=RequestContext(request))
    
@login_required
def delete_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    if offer.offerer != request.user:
        request.user.message_set.create(message="You cannot delete offers that are not yours")
        return HttpResponseRedirect(reverse("offer_list_yours"))
    if request.method == "POST":
        offer.delete()
    return HttpResponseRedirect(reverse("offer_list_yours"))

@login_required
def cancel_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    if offer.offerer != request.user:
        request.user.message_set.create(message="You cannot cancel offers that are not yours")
        return HttpResponseRedirect(reverse("offer_list_yours"))
    if request.method == "POST":
        offer.cancel()
    return HttpResponseRedirect(reverse("offer_list_yours"))

@login_required
def propose_swap(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    if request.method == "POST":
        swap_form = ProposeSwapForm(request.POST)
        offer_form = ProposingOfferForm(request.POST)
        swap = None
        if swap_form.is_valid():
            swap = swap_form.save(commit=False)
            swap.responding_offer = offer
            swap.save()
        if offer_form.is_valid():
            proposing_offer = offer_form.save(commit=False)
            proposing_offer.offerer = request.user
            proposing_offer.save()
            swap = Swap(
                proposing_offer=proposing_offer,
                responding_offer=offer)
            swap.save()
        if swap:
            if notification:
                notification.send([offer.offerer,], "swaps_proposal", 
                    {"creator": request.user, 
                     "swap": swap, 
                     "proposing_offer": swap.proposing_offer, 
                     "responding_offer": swap.responding_offer}) 
            return HttpResponseRedirect(reverse("proposed_by_you"))            
    else:
        swap_form = ProposeSwapForm()
        swap_form.fields['proposing_offer'].queryset = Offer.objects.filter(offerer=request.user, state=1)
        offer_form = ProposingOfferForm()
    return render_to_response("swaps/propose_swap.html", {
        "offer": offer,
        "swap_form": swap_form,
        "offer_form": offer_form,
    }, context_instance=RequestContext(request))
    
@login_required
def accept_swap(request, swap_id):
    swap = get_object_or_404(Swap, id=swap_id)
    swap.accept()
    swap.save()
    if notification:
        notification.send([swap.proposing_offer.offerer,], "swaps_acceptance", 
            {"creator": request.user, 
             "swap": swap, 
             "proposing_offer": swap.proposing_offer, 
             "responding_offer": swap.responding_offer})
    return HttpResponseRedirect(reverse("accepted_swaps"))

@login_required
def reject_swap(request, swap_id):
    swap = get_object_or_404(Swap, id=swap_id)
    swap.reject()
    swap.save()
    if notification:
        notification.send([swap.proposing_offer.offerer,], "swaps_rejection", 
            {"creator": request.user, 
             "swap": swap, 
             "proposing_offer": swap.proposing_offer, 
             "responding_offer": swap.responding_offer})
    return HttpResponseRedirect(reverse("dead_swaps"))

@login_required
def cancel_swap(request, swap_id):
    swap = get_object_or_404(Swap, id=swap_id)
    swap.cancel()
    swap.save()
    if notification:
        notification.send([swap.responding_offer.offerer,], "swaps_cancellation", 
            {"creator": request.user, 
             "swap": swap, 
             "proposing_offer": swap.proposing_offer, 
             "responding_offer": swap.responding_offer})
    return HttpResponseRedirect(reverse("dead_swaps"))

