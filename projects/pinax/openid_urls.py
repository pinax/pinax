from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^signup/$', 'django_openidauth.regviews.register', {
        'success_url': '/account/',
        'template_name': 'openid/signup.html',
        'already_registered_url': '/account/',
    }),
    (r'^login/$', 'django_openidconsumer.views.begin', {
        'sreg': 'email,nickname',
        'redirect_to': '/openid/complete/'
    }),
    (r'^complete/$', 'django_openidauth.views.complete', {
        'on_login_ok_url'    : '/',
        'on_login_failed_url': '/openid/signup/'
    }),
    (r'^signout/$', 'django_openidconsumer.views.signout'),
    (r'^associations/$', 'django_openidauth.views.associations', {
        'template_name': 'openid/associations.html',
    }),
)