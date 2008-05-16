from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User

from friends.forms import InviteFriendForm
from friends.models import FriendshipInvitation

def profiles(request):
    return render_to_response("profiles/profiles.html", {
        "users": User.objects.all(),
    }, context_instance=RequestContext(request))

def profile(request, username):
    other_user = get_object_or_404(User, username=username)
    if request.method == "POST":
        invite_form = InviteFriendForm(request.user, request.POST)
        if invite_form.is_valid():
            invite_form.save()
    else:
        invite_form = InviteFriendForm(request.user, {
            'to_user': username,
        })
    previous_invitations = FriendshipInvitation.objects.filter(to_user=other_user, from_user=request.user)
    return render_to_response("profiles/profile.html", {
        "other_user": other_user,
        "invite_form": invite_form,
        "previous_invitations": previous_invitations,
    }, context_instance=RequestContext(request))
