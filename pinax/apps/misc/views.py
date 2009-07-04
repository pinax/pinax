from django.http import HttpResponse, HttpResponseForbidden
from django.conf import settings

# @@@ these can be cleaned up a lot, made more generic and with better queries

def username_autocomplete_all(request):
    if request.user.is_authenticated():
        from django.contrib.auth.models import User
        from basic_profiles.models import Profile
        from avatar.templatetags.avatar_tags import avatar
        q = request.GET.get("q")
        users = User.objects.all()
        content = []
        # @@@ temporary hack -- don't try this at home (or on real sites)
        for user in users:
            if user.username.lower().startswith(q):
                try:
                    profile = user.get_profile()
                    entry = "%s,,%s,,%s" % (
                        avatar(user, 40),
                        user.username,
                        profile.location
                    )
                except Profile.DoesNotExist:
                    pass
                content.append(entry)
        response = HttpResponse("\n".join(content))
    else:
        response = HttpResponseForbidden()
    setattr(response, "djangologging.suppress_output", True)
    return response


def username_autocomplete_friends(request):
    if request.user.is_authenticated():
        from friends.models import Friendship
        from profiles.models import Profile
        from avatar.templatetags.avatar_tags import avatar
        q = request.GET.get("q")
        friends = Friendship.objects.friends_for_user(request.user)
        content = []
        for friendship in friends:
            if friendship["friend"].username.lower().startswith(q):
                try:
                    profile = friendship["friend"].get_profile()
                    entry = "%s,,%s,,%s" % (
                        avatar(friendship["friend"], 40),
                        friendship["friend"].username,
                        profile.location
                    )
                except Profile.DoesNotExist:
                    pass
                content.append(entry)
        response = HttpResponse("\n".join(content))
    else:
        response = HttpResponseForbidden()
    setattr(response, "djangologging.suppress_output", True)
    return response
