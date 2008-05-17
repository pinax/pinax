from django.shortcuts import render_to_response
from django.template import RequestContext
from notification.models import Notice

def notices(request):
    if request.user.is_authenticated():
        notices = Notice.objects.filter(user=request.user).order_by("-added")
    else:
        notices = None
    return render_to_response("notices_app/notices.html", {
        "notices": notices,
    }, context_instance=RequestContext(request))
