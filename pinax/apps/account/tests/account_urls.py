from django.conf.urls.defaults import *


urlpatterns = patterns("",
    url(r"^account/", include("pinax.apps.account.urls")),
    url(r"^$", "pinax.apps.account.views.login", name="home") #need a home to correctly render the template..
)
