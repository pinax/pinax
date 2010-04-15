from django.conf.urls.defaults import *



urlpatterns = patterns("",
    url(r"^$", "contacts.views.contacts", name="contacts"),
    (r"^import/", include("contacts_import.urls")),
)
