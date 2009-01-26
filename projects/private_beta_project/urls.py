from django.conf.urls.defaults import *
from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.views.generic.simple import direct_to_template

from account.openid_consumer import PinaxConsumer
from waitinglist.forms import WaitingListEntryForm

from django.contrib import admin
admin.autodiscover()

import os

def homepage(request):
    if request.method == "POST":
        form = WaitingListEntryForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("waitinglist_sucess"))
    else:
        form = WaitingListEntryForm()
    return direct_to_template(request, "homepage.html", {
        "form": form,
    })

urlpatterns = patterns('',
    url(r'^$', homepage, name="home"),
    url(r'^success/$', direct_to_template, {"template": "waitinglist/success.html"}, name="waitinglist_sucess"),
    
    (r'^about/', include('about.urls')),
    (r'^account/', include('account.urls')),
    (r'^openid/(.*)', PinaxConsumer()),
    (r'^profiles/', include('basic_profiles.urls')),
    (r'^notices/', include('notification.urls')),
    (r'^announcements/', include('announcements.urls')),
    
    (r'^admin/(.*)', admin.site.root),
)

if settings.SERVE_MEDIA:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': os.path.join(os.path.dirname(__file__), "site_media")}),
    )
