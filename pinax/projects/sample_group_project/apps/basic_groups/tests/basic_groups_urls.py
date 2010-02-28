from django.conf.urls.defaults import *


urlpatterns = patterns("",
    url(r"^groups/", include("basic_groups.urls")),
    url(r"^profiles/", include("pinax.apps.profiles.urls")),
)
