from django.conf.urls.defaults import *

urlpatterns = \
    patterns('',
        url(r'^create/$', 'basic_groups.views.create', name="group_create"),
        url(r'^your_groups/$', 'basic_groups.views.your_groups', name="your_groups"),
        
        url(r'^$', 'basic_groups.views.groups', name="group_list"), 
        url(r'^order/(?P<order>\w+)/$', 'basic_groups.views.groups', name="group_list_order"),
        
        # group-specific
        url(r'^group/([-\w]+)/$', 'basic_groups.views.group', name="group_detail"),
        url(r'^group/([-\w]+)/delete/$', 'basic_groups.views.delete', name="group_delete"),
    )