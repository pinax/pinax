from django.conf.urls.defaults import *
from django.conf import settings

from django.shortcuts import render_to_response
from django.template import RequestContext

def static_view(request, path):
    """
    serve pages directly from the templates directories.
    """
    template_name = path + "index.html" if not path or path.endswith("/") else path
    return render_to_response(template_name, context_instance=RequestContext(request))

urlpatterns = patterns("",
    (r"^(.*)$", static_view)
)

if settings.SERVE_MEDIA:
    urlpatterns = patterns('',
        (r'^site_media/', include('staticfiles.urls')),
    ) + urlpatterns
