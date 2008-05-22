from django.shortcuts import render_to_response
from django.template import RequestContext
from notification.models import notices_for

def notices(request):
    if request.user.is_authenticated():
        notices = notices_for(request.user)
    else:
        notices = None
    return render_to_response("notices_app/notices.html", {
        "notices": notices,
    }, context_instance=RequestContext(request))
