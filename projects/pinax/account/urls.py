from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'account.views.account'),
    (r'^signup/$', 'account.views.signup'),
    (r'^login/$', 'account.views.login'),
    (r'^password_reset/$', 'account.views.password_reset'),
    (r'^logout/$', 'django.contrib.auth.views.logout', {"template_name": "account/logout.html"}),
    
    (r'^confirm_email/(\w+)/$', 'emailconfirmation.views.confirm_email'),
)
