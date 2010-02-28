from django.conf.urls.defaults import *



urlpatterns = patterns("",
    url(r"^tasks/", include("pinax.apps.tasks.urls")),
    url(r"^notices/", include("notification.urls")),
    url(r"^tagging_utils/", include("pinax.apps.tagging_utils.urls")),
    url(r"^comments/", include("threadedcomments.urls")),
)
