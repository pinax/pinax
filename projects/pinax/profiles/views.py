from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User

from friends.forms import InviteFriendForm
from friends.models import FriendshipInvitation, Friendship

def profiles(request):
    return render_to_response("profiles/profiles.html", {
        "users": User.objects.all().order_by("-date_joined"),
    }, context_instance=RequestContext(request))

def profile(request, username):
    other_user = get_object_or_404(User, username=username)
    if request.user.is_authenticated():
        is_friend = Friendship.objects.are_friends(request.user, other_user)
        other_friends = Friendship.objects.friends_for_user(other_user)
    else:
        other_friends = []
        is_friend = False
    if is_friend:
        invite_form = None
        previous_invitations_to = None
        previous_invitations_from = None
    else:
        if request.method == "POST":
            if request.POST["action"] == "invite":
                invite_form = InviteFriendForm(request.user, request.POST)
                if invite_form.is_valid():
                    invite_form.save()
            else:
                invite_form = InviteFriendForm(request.user, {
                    'to_user': username,
                })
                if request.POST["action"] == "accept":
                    invitation_id = request.POST["invitation"]
                    try:
                        invitation = FriendshipInvitation.objects.get(id=invitation_id)
                        if invitation.to_user == request.user:
                            invitation.accept()
                            request.user.message_set.create(message="Accepted friendship request from %s" % invitation.from_user)
                    except FriendshipInvitation.DoesNotExist:
                        pass
        else:
            invite_form = InviteFriendForm(request.user, {
                'to_user': username,
            })
    previous_invitations_to = FriendshipInvitation.objects.filter(to_user=other_user, from_user=request.user)
    previous_invitations_from = FriendshipInvitation.objects.filter(to_user=request.user, from_user=other_user)
    
    return render_to_response("profiles/profile.html", {
        "is_friend": is_friend,
        "other_user": other_user,
        "other_friends": other_friends,
        "invite_form": invite_form,
        "previous_invitations_to": previous_invitations_to,
        "previous_invitations_from": previous_invitations_from,
    }, context_instance=RequestContext(request))
