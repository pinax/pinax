from django.conf.urls.defaults import patterns, url, include

handler500 = "pinax.views.server_error"

urlpatterns = patterns("",
    (r"^tags/$", "tagging_ext.views.index"),
    url(r"^profiles/", include("idios.urls")),
)
