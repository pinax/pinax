from django.conf.urls.defaults import patterns, url, include, handler404, handler500


urlpatterns = patterns("",
    (r"^tags/$", "tagging_ext.views.index"),
    url(r"^profiles/", include("idios.urls")),
)
