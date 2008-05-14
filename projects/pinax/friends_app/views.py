from django.shortcuts import render_to_response
from django.template import RequestContext
from friends.models import Friendship

def friends(request):
    return render_to_response("friends_app/friends.html", {
        "friends": Friendship.objects.friends_for_user(request.user),
    }, context_instance=RequestContext(request))
    