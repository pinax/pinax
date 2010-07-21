from django.conf import settings
from django.conf.urls.defaults import *
from django.shortcuts import render_to_response
from django.template import RequestContext


handler500 = "pinax.views.server_error"


urlpatterns = patterns("",
    (r"^(.*)$", "pinax.views.static_view")
)


if settings.SERVE_MEDIA:
    urlpatterns = patterns("",
        (r"", include("staticfiles.urls")),
    ) + urlpatterns
