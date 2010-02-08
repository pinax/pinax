from django.conf.urls.defaults import *


urlpatterns = patterns("",
    url(r'^account/', include('account.urls')),
)