from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User

def profile(request, username):
    other_user = get_object_or_404(User, username=username)
    return render_to_response("profiles/profile.html", {
        "other_user": other_user,
    }, context_instance=RequestContext(request))
