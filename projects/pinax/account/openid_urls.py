from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^signup/$', 'django_openidauth.regviews.register', {
        'success_url': '/account/email/',
        'template_name': 'openid/signup.html',
        'already_registered_url': '/openid/associations/',
    }, name="openid_signup"),
    url(r'^login/$', 'django_openidconsumer.views.begin', {
        'sreg': 'email,nickname',
        'redirect_to': '/openid/complete/'
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