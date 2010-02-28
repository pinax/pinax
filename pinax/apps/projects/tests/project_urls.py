from django.conf.urls.defaults import *


urlpatterns = patterns("",
    url(r"^projects/", include("pinax.apps.projects.urls")),
    url(r"^profiles/", include("pinax.apps.profiles.urls")),
)
