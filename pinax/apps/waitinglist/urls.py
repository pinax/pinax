from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template


urlpatterns = patterns("",
    url(r"^list_signup/$", "pinax.apps.waitinglist.views.list_signup", name="waitinglist_list_signup"),
    url(r"^success/$", direct_to_template, {"template": "waitinglist/success.html"}, name="waitinglist_success"),
)