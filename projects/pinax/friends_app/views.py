from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.conf import settings

from django.utils.translation import ugettext_lazy as _

from friends.models import *
from friends.forms import JoinRequestForm
from account.forms import SignupForm

# @@@ if made more generic these could be moved to django-friends proper

def friends(request):
    if request.user.is_authenticated():
        if request.method == "POST":
            if request.POST["action"] == "accept":
                invitation_id = request.POST["invitation"]
                try:
                    invitation = FriendshipInvitation.objects.get(id=invitation_id)
                    if invitation.to_user == request.user:
                        invitation.accept()
                        request.user.message_set.create(message=_("Accepted friendship request from %(from_user)s") % {'from_user': invitation.from_user})
                except FriendshipInvitation.DoesNotExist:
                    pass
            elif request.POST["action"] == "invite": # invite to join
                join_request_form = JoinRequestForm(request.POST)
                if join_request_form.is_valid():
                    join_request_form.save(request.user)
                    join_request_form = JoinRequestForm() # @@@
        else:
            join_request_form = JoinRequestForm()
    else:
        join_request_form = None
    return render_to_response("friends_app/invitations.html", {
        "join_request_form": join_request_form,
    }, context_instance=RequestContext(request))


def accept_join(request, confirmation_key):
    join_invitation = get_object_or_404(JoinInvitation, confirmation_key = confirmation_key.lower())
    if request.user.is_authenticated():
        return render_to_response("account/signup.html", {
            "contact_email": settings.CONTACT_EMAIL,
        }, context_instance=RequestContext(request))
    else:
        form = SignupForm(initial={"email": join_invitation.contact.email, "confirmation_key": join_invitation.confirmation_key })
        return render_to_response("account/signup.html", {
            "form": form,
            "contact_email": settings.CONTACT_EMAIL,
        }, context_instance=RequestContext(request))
