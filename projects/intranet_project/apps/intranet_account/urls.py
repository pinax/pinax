from django.conf.urls.defaults import *
from intranet_account.forms import *

urlpatterns = patterns('',
    url(r'^email/$', 'intranet_account.views.email', name="acct_email"),
    url(r'^login/$', 'intranet_account.views.login', name="acct_login"),
    url(r'^password_change/$', 'intranet_account.views.password_change', name="acct_passwd"),
    url(r'^password_set/$', 'intranet_account.views.password_set', name="acct_passwd_set"),
    url(r'^password_delete/$', 'intranet_account.views.password_delete', name="acct_passwd_delete"),
    url(r'^password_delete/done/$', 'django.views.generic.simple.direct_to_template', {
        "template": "account/password_delete_done.html",
    }, name="acct_passwd_delete_done"),
    url(r'^password_reset/$', 'intranet_account.views.password_reset', name="acct_passwd_reset"),
    url(r'^timezone/$', 'intranet_account.views.timezone_change', name="acct_timezone_change"),
    url(r'^other_services/$', 'intranet_account.views.other_services', name="acct_other_services"),
    url(r'^language/$', 'intranet_account.views.language_change', name="acct_language_change"),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {"template_name": "account/logout.html"}, name="acct_logout"),
    
    url(r'^confirm_email/(\w+)/$', 'emailconfirmation.views.confirm_email', name="acct_confirm_email"),

    # ajax validation
    (r'^validate/$', 'ajax_validation.views.validate', {'form_class': SignupForm}, 'signup_form_validate'),
)
