from django.utils.translation import ugettext as _
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.conf import settings

def simple_basic_auth_callback(request, user, *args, **kwargs):
    """
    Simple callback to automatically login the given user after a successful
    basic authentication.
    """
    login(request, user)
    request.user = user

def basic_auth_required(realm=None, test_func=None, callback_func=None):
    """
    This decorator should be used with views that need simple authentication
    against Django's authentication framework.
    
    The ``realm`` string is shown during the basic auth query.
    
    It takes a ``test_func`` argument that is used to validate the given
    credentials and return the decorated function if successful.
    
    If unsuccessful the decorator will try to authenticate and checks if the
    user has the ``is_active`` field set to True.
    
    In case of a successful authentication  the ``callback_func`` will be
    called by passing the ``request`` and the ``user`` object. After that the
    actual view function will be called.
    
    If all of the above fails a "Authorization Required" message will be shown.
    """
    if realm is None:
        realm = getattr(settings, 'HTTP_AUTHENTICATION_REALM', _('Restricted Access'))
    if test_func is None:
        test_func = lambda u: u.is_authenticated()

    def decorator(view_func):
        def basic_auth(request, *args, **kwargs):
            # Just return the original view because already logged in
            if test_func(request.user):
                return view_func(request, *args, **kwargs)

            # Not logged in, look if login credentials are provided
            if 'HTTP_AUTHORIZATION' in request.META:        
                auth_method, auth = request.META['HTTP_AUTHORIZATION'].split(' ',1)
                if 'basic' == auth_method.lower():
                    auth = auth.strip().decode('base64')
                    username, password = auth.split(':',1)
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        if user.is_active:
                            if callback_func is not None and callable(callback_func):
                                callback_func(request, user, *args, **kwargs)
                            return view_func(request, *args, **kwargs)

            response =  HttpResponse(_('Authorization Required'), mimetype="text/plain")
            response.status_code = 401
            response['WWW-Authenticate'] = 'Basic realm="%s"' % realm
            return response
        return basic_auth
    return decorator
