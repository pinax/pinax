# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.utils.translation import ugettext as _

urlpatterns = patterns('authopenid.views',
     # manage account registration
    url(r'^%s$' % _('signin/'), 'signin', name='user_signin'),
    url(r'^%s$' % _('signout/'), 'signout', name='user_signout'),
    url(r'^%s%s$' % (_('signin/'), _('complete/')), 'complete_signin', name='user_complete_signin'),
    url(r'^%s$' % _('register/'), 'register', name='user_register'),
    url(r'^%s$' % _('signup/'), 'signup', name='user_signup'),
    url(r'^%s$' % _('password/'), 'sendpw', name='user_sendpw'),
    url(r'^%s%s$' % (_('password/'), _('confirm/')), 'confirmchangepw', name='user_confirmchangepw'),

    # manage account settings
    url(r'^(?P<username>\w+)/$', 'account_settings', name='user_account_settings'),
    url(r'^$', 'account_settings', name='user_account_settings'),
    url(r'^(?P<username>\w+)/%s$' % _('password/'), 'changepw', name='user_changepw'),
    url(r'^(?P<username>\w+)/%s$' % _('email/'), 'changeemail', name='user_changeemail'),
    url(r'^(?P<username>\w+)/%s$' % _('openid/'), 'changeopenid', name='user_changeopenid'),
    url(r'^(?P<username>\w+)/%s$' % _('delete/'), 'delete', name='user_delete'),
    
    
)
