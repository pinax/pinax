from django.conf import settings
from django.conf.urls.defaults import *
from django.shortcuts import render_to_response
from django.template import RequestContext



def static_view(request, path):
    """
    serve pages directly from the templates directories.
    """
    if not path or path.endswith("/"):
        template_name = path + "index.html"
    else:
        template_name = path
    return render_to_response(template_name, RequestContext(request))


urlpatterns = patterns("",
    (r"^(.*)$", static_view)
)


if settings.SERVE_MEDIA:
    urlpatterns = patterns("",
        (r"", include("staticfiles.urls")),
    ) + urlpatterns
