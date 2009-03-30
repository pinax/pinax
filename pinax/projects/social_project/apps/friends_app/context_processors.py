from friends.models import FriendshipInvitation

def invitations(request):
    if request.user.is_authenticated():
        return {'invitations_count': FriendshipInvitation.objects.filter(to_user=request.user, status="2").count(),}
    else:
        return {}
