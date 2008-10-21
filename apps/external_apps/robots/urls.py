from django.conf.urls.defaults import *
from robots.views import rules_list

urlpatterns = patterns('',
    url(r'^$', rules_list, name='robots_rule_list'),
)
