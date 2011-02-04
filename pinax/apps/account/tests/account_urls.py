from django.conf.urls.defaults import *


urlpatterns = patterns("",
    url(r'^account/', include('pinax.apps.account.urls')),
)
