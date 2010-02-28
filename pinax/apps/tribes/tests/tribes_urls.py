from django.conf.urls.defaults import *


urlpatterns = patterns("",
    url(r"^tribes/", include("pinax.apps.tribes.urls")),
    url(r"^profiles/", include("pinax.apps.profiles.urls")),
)
