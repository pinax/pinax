from django.conf import settings
from django.core import signals
from django.dispatch import dispatcher
import re
MASK_IN_EXCEPTION_EMAIL= ['password', 'mail', 'protected', 'private' ]

mask_re = re.compile('(' + '|'.join(MASK_IN_EXCEPTION_EMAIL) + ')', re.I)

def clean_request_for_except_repr(signal=None, sender=None, request=None):
    if not request or not request.POST or setings.DEBUG: return False
    masked = False
    mutable = True
    if hasattr(request.POST, '_mutable'):
        mutable = request.POST._mutable
        request.POST._mutable = True
    for name in request.POST:
        if mask_re.search(name):
            request.POST[name]=u'xxHIDDENxx'
            masked=True
    if hasattr(request.POST, '_mutable'):
        request.POST._mutable = mutable
    return masked

def insert_svn_app_versions(signal=None, sender=None, request=None):
    if not request or not request.META: return False
    try:
        from templatetags.svn_app_version import get_all_versions
    except:
        return False
    mutable = True
    if hasattr(request.META, '_mutable'):
        mutable = request.META._mutable
        request.META._mutable = True
    added = False
    print "HELLO!", get_all_versions(False)
    prefix = 'svn_app_version'
    for app, version in get_all_versions(True):
        request.META[prefix + app] = version
        prefix = 'svn_app_version.'
        added=True
    if hasattr(request.META, '_mutable'):
        request.META._mutable = mutable
    return added

dispatcher.connect(clean_request_for_except_repr,
                   signal=signals.got_request_exception)
dispatcher.connect(insert_svn_app_versions,
                   signal=signals.got_request_exception)
