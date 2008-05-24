from django.shortcuts import render_to_response
from django.template import RequestContext
from friends.models import Friendship, FriendshipInvitation

def friends(request):
    if request.user.is_authenticated():
        if request.method == "POST":
            if request.POST["action"] == "accept":
                invitation_id = request.POST["invitation"]
                try:
                    invitation = FriendshipInvitation.objects.get(id=invitation_id)
                    if invitation.to_user == request.user:
                        invitation.accept()
                        request.user.message_set.create(message="Accepted friendship request from %s" % invitation.from_user)
                except FriendshipInvitation.DoesNotExist:
                    pass
    return render_to_response("friends_app/invitations.html", {
    }, context_instance=RequestContext(request))
    