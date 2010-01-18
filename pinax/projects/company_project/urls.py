from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()



# override the default handler500 so i can pass MEDIA_URL
handler500 = "company_project.views.server_error"



urlpatterns = patterns("",
    url(r"^$", direct_to_template, {"template": "homepage.html"}, name="home"),
    
    url(r"^blog/", include("biblion.urls")),
    url(r"^feed/$", "biblion.views.blog_feed", name="blog_feed_combined"),
    url(r"^feed/(?P<section>[-\w]+)/$", "biblion.views.blog_feed", name="blog_feed"),
    
    url(r"^admin/(.*)", admin.site.root),
)


if settings.SERVE_MEDIA:
    urlpatterns += patterns("",
        (r"", include("staticfiles.urls")),
    )
