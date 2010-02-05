from django.conf.urls.defaults import *



urlpatterns = patterns("",
    url(r"^tasks/", include("pinax.apps.tasks.urls")),
)