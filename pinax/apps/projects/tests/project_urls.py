from django.conf.urls.defaults import *


urlpatterns = patterns("",
    url(r"^projects/", include("pinax.apps.projects.urls")),
)