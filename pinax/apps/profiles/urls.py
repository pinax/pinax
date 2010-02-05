from django.conf.urls.defaults import *



urlpatterns = patterns("",
    url(r"^username_autocomplete/$", "pinax.apps.autocomplete_app.views.username_autocomplete_friends", name="profile_username_autocomplete"),
    url(r"^$", "pinax.apps.profiles.views.profiles", name="profile_list"),
    url(r"^profile/(?P<username>[\w\._-]+)/$", "pinax.apps.profiles.views.profile", name="profile_detail"),
    url(r"^edit/$", "pinax.apps.profiles.views.profile_edit", name="profile_edit"),
)
