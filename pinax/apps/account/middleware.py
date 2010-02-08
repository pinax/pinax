import re

from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils import translation
from django.utils.cache import patch_vary_headers
from django.utils.http import urlquote

from django.contrib.auth import REDIRECT_FIELD_NAME

from account.models import Account



class LocaleMiddleware(object):
    """
    This is a very simple middleware that parses a request
    and decides what translation object to install in the current
    thread context depending on the user"s account. This allows pages
    to be dynamically translated to the language the user desires
    (if the language is available, of course).
    """
    
    def get_language_for_user(self, request):
        if request.user.is_authenticated():
            try:
                account = Account.objects.get(user=request.user)
                return account.language
            except Account.DoesNotExist:
                pass
        return translation.get_language_from_request(request)
    
    def process_request(self, request):
        translation.activate(self.get_language_for_user(request))
        request.LANGUAGE_CODE = translation.get_language()
    
    def process_response(self, request, response):
        patch_vary_headers(response, ("Accept-Language",))
        response["Content-Language"] = translation.get_language()
        translation.deactivate()
        return response


class AuthenticatedMiddleware(object):
    def __init__(self, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
        if login_url is None:
            login_url = settings.LOGIN_URL
        self.redirect_field_name = redirect_field_name
        self.login_url = login_url
        self.exemptions = [
            r"^%s" % settings.MEDIA_URL,
            r"^%s" % settings.STATIC_URL,
            r"^%s$" % login_url,
        ] + getattr(settings, "AUTHENTICATED_EXEMPT_URLS", [])
    
    def process_request(self, request):
        for exemption in self.exemptions:
            if re.match(exemption, request.path):
                return None
        if not request.user.is_authenticated():
            path = urlquote(request.get_full_path())
            tup = (self.login_url, self.redirect_field_name, path)
            return HttpResponseRedirect("%s?%s=%s" % tup)
