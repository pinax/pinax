from django.conf.urls.defaults import *

urlpatterns = patterns('',
    
    (r'^accounts/', include('authopenid.urls')),
    
    # Uncomment this for admin:
    (r'^admin/', include('django.contrib.admin.urls')),
)
