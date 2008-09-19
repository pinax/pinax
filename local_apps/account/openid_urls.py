from django.conf.urls.defaults import *
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django_openidauth.regviews import register

def if_not_user_url(request):
    return HttpResponseRedirect(reverse('acct_login'))

def restrict_signup(func):
    def _inner(request, *args, **kwargs):
        if not request.openid:
            return HttpResponseRedirect(reverse('acct_login'))
        return register(request, *args, **kwargs)
    return _inner

urlpatterns = patterns('',
    url(r'^signup/$', restrict_signup(register), {
        'success_url': '/account/email/',
        'template_name': 'openid/signup.html',
        'already_registered_url': '/openid/associations/',
    }, name="openid_signup"),
    url(r'^login/$', 'django_openidconsumer.views.begin', {
        'sreg': 'email,nickname',
        'redirect_to': '/openid/complete/',
        'if_not_user_url': if_not_user_url,
    }, name="openid_login"),
    url(r'^complete/$', 'django_openidauth.views.complete', {
        'on_login_ok_url'    : '/',
        'on_login_failed_url': '/openid/signup/'
    }, name="openid_complete"),
    url(r'^logout/$', 'django_openidconsumer.views.signout', name="openid_logout"),
    url(r'^associations/$', 'django_openidauth.views.associations', {
        'template_name': 'openid/associations.html',
    }, name="openid_assoc"),
)