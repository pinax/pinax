import urlparse

from openid import oidutil

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext

from django.contrib import messages

from django_openid.registration import RegistrationConsumer

from pinax.apps.account.forms import OpenIDSignupForm
from pinax.apps.account.utils import get_default_redirect, user_display
from pinax.apps.account.views import login as account_login



# install our own logger that does nothing
def dummy_log(*args, **kwargs):
    return
oidutil.log = dummy_log



class PinaxConsumer(RegistrationConsumer):
    
    # Pinax does its own e-mail confirmation handling, but django-openid
    # wants to do its own handling of this so we turn it off in all cases
    confirm_email_addresses = False
    
    redirect_field_name = "next"
    
    def on_registration_complete(self, request):
        if hasattr(settings, "LOGIN_REDIRECT_URLNAME"):
            fallback_url = reverse(settings.LOGIN_REDIRECT_URLNAME)
        else:
            fallback_url = settings.LOGIN_REDIRECT_URL
        return HttpResponseRedirect(get_default_redirect(request, fallback_url))
    
    def show_i_have_logged_you_in(self, request):
        if hasattr(settings, "LOGIN_REDIRECT_URLNAME"):
            fallback_url = reverse(settings.LOGIN_REDIRECT_URLNAME)
        else:
            fallback_url = settings.LOGIN_REDIRECT_URL
        return HttpResponseRedirect(get_default_redirect(request, fallback_url))
    
    def get_registration_form_class(self, request):
        return OpenIDSignupForm
    
    def do_register(self, request, message=None):
        """
        do_register implementation is copied from django-openid so we can
        ensure Pinax functionality in OpenID registration. django-openid
        didn't quite give enough hooks.
        
        This implementation modifies the POST case and will not run
        create_user, confirm_email_step or on_registration_complete hooks.
        """
        # Show a registration / signup form, provided the user is not
        # already logged in
        if not request.user.is_anonymous():
            return self.show_already_signed_in(request)
        
        openid_url = request.POST.get("openid_url")
        openids = request.session.get("openids")
        
        if not openid_url and not openids:
            return account_login(request, url_required=True, extra_context={
                "openid_login": True,
            })
        
        # perform OpenID login if openid_url is defined. we do this before the
        # check to ACCOUNT_OPEN_SIGNUP to allow users who have existing OpenID
        # association to login even when ACCOUNT_OPEN_SIGNUP is turned off.
        if openid_url:
            return self.start_openid_process(request,
                user_url = openid_url,
                on_complete_url = urlparse.urljoin(
                    request.path, "../register_complete/"
                ),
                trust_root = urlparse.urljoin(request.path, "..")
            )
        
        if not settings.ACCOUNT_OPEN_SIGNUP:
            return render_to_response("django_openid/registration_closed.html", {
            }, context_instance=RequestContext(request))
        
        RegistrationForm = self.get_registration_form_class(request)
        
        try:
            openid = request.openid and request.openid.openid or None
        except AttributeError:
            return self.show_error(
                request, "Add CookieConsumer or similar to your middleware"
            )
        
        if request.method == "POST":
            # TODO: The user might have entered an OpenID as a starting point,
            # or they might have decided to sign up normally
            form = RegistrationForm(
                request.POST,
                openid = openid,
                reserved_usernames = self.reserved_usernames,
                no_duplicate_emails = self.no_duplicate_emails
            )
            if form.is_valid():
                # Pinax modification
                user = form.save(request=request)
                if openid:
                    user.openids.create(openid=openid)
                if settings.ACCOUNT_EMAIL_VERIFICATION:
                    return render_to_response("account/verification_sent.html", {
                        "email": form.cleaned_data["email"],
                    }, context_instance=RequestContext(request))
                else:
                    # form.login is the same implementation used in normal
                    # signup. hopefully this doesn't bite us later.
                    self.log_in_user(request, user)
                    messages.add_message(request, messages.SUCCESS,
                        ugettext("Successfully logged in as %(user)s.") % {
                            "user": user_display(user)
                        }
                    )
                    # @@@ honor custom redirect more fully (this is used primarily for
                    # the default fallback)
                    if hasattr(settings, "SIGNUP_REDIRECT_URLNAME"):
                        fallback_url = reverse(settings.SIGNUP_REDIRECT_URLNAME)
                    else:
                        if hasattr(settings, "LOGIN_REDIRECT_URLNAME"):
                            fallback_url = reverse(settings.LOGIN_REDIRECT_URLNAME)
                        else:
                            fallback_url = settings.LOGIN_REDIRECT_URL
                    success_url = get_default_redirect(request, fallback_url, self.redirect_field_name)
                    return HttpResponseRedirect(success_url)
        else:
            form = RegistrationForm(
                initial = request.openid and self.initial_from_sreg(
                    request.openid.sreg
                ) or {},
                openid = openid,
                reserved_usernames = self.reserved_usernames,
                no_duplicate_emails = self.no_duplicate_emails
            )
        
        return self.render(request, self.register_template, {
            "form": form,
            "message": message,
            "openid": request.openid,
            "logo": self.logo_path or (urlparse.urljoin(
                request.path, "../logo/"
            )),
            "no_thanks": self.sign_next(request.path),
            "action": request.path,
        })
    
    def show_already_signed_in(self, request):
        return render_to_response("django_openid/already_logged_in.html", {
        }, context_instance=RequestContext(request))