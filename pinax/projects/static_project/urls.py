from django.conf import settings
from django.conf.urls.defaults import *
from django.conf.urls.static import static
from django.shortcuts import render_to_response
from django.template import RequestContext

from staticfiles.urls import staticfiles_urlpatterns


handler500 = "pinax.views.server_error"


urlpatterns = patterns("",
    (r"^(.*)$", "pinax.views.static_view")
)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
