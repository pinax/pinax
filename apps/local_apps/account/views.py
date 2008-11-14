
from django.conf import settings
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from account.forms import SignupForm, AddEmailForm, LoginForm, ChangePasswordForm, SetPasswordForm, ResetPasswordForm, ChangeTimezoneForm, ChangeLanguageForm, TwitterForm, PownceForm
from emailconfirmation.models import EmailAddress, EmailConfirmation

def login(request, form_class=LoginForm, template_name="account/login.html"):
    if request.method == "POST":
        default_redirect_to = getattr(settings, "LOGIN_REDIRECT_URLNAME", None)
        if default_redirect_to:
            default_redirect_to = reverse(default_redirect_to)
        else:
            default_redirect_to = settings.LOGIN_REDIRECT_URL
        redirect_to = request.REQUEST.get("next")
        # light security check -- make sure redirect_to isn't garabage.
        if not redirect_to or "://" in redirect_to or " " in redirect_to:
            redirect_to = default_redirect_to
        form = form_class(request.POST)
        if form.login(request):
            return HttpResponseRedirect(redirect_to)
    else:
        form = form_class()
    return render_to_response(template_name, {
        "form": form,
    }, context_instance=RequestContext(request))

def signup(request, form_class=SignupForm,
        template_name="account/signup.html", success_url=None):
    if success_url is None:
        success_url = reverse("what_next")
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            username, password = form.save()
            user = authenticate(username=username, password=password)
            auth_login(request, user)
            request.user.message_set.create(message=_("Successfully logged in as %(username)s.") % {'username': user.username})
            return HttpResponseRedirect(success_url)
    else:
        form = form_class()
    return render_to_response(template_name, {
        "form": form,
    }, context_instance=RequestContext(request))

def email(request, form_class=AddEmailForm,
        template_name="account/email.html"):
    if request.method == "POST" and request.user.is_authenticated():
        if request.POST["action"] == "add":
            add_email_form = form_class(request.user, request.POST)
            if add_email_form.is_valid():
                add_email_form.save()
                add_email_form = form_class() # @@@
        else:
            add_email_form = form_class()
            if request.POST["action"] == "send":
                email = request.POST["email"]
                try:
                    email_address = EmailAddress.objects.get(user=request.user, email=email)
                    request.user.message_set.create(message="Confirmation email sent to %s" % email)
                    EmailConfirmation.objects.send_confirmation(email_address)
                except EmailAddress.DoesNotExist:
                    pass
            elif request.POST["action"] == "remove":
                email = request.POST["email"]
                try:
                    email_address = EmailAddress.objects.get(user=request.user, email=email)
                    email_address.delete()
                    request.user.message_set.create(message="Removed email address %s" % email)
                except EmailAddress.DoesNotExist:
                    pass
            elif request.POST["action"] == "primary":
                email = request.POST["email"]
                email_address = EmailAddress.objects.get(user=request.user, email=email)
                email_address.set_as_primary()
    else:
        add_email_form = form_class()
    return render_to_response(template_name, {
        "add_email_form": add_email_form,
    }, context_instance=RequestContext(request))
email = login_required(email)

def password_change(request, form_class=ChangePasswordForm,
        template_name="account/password_change.html"):
    if not request.user.password:
        return HttpResponseRedirect(reverse("acct_passwd_set"))
    if request.method == "POST":
        password_change_form = form_class(request.user, request.POST)
        if password_change_form.is_valid():
            password_change_form.save()
            password_change_form = form_class(request.user)
    else:
        password_change_form = form_class(request.user)
    return render_to_response(template_name, {
        "password_change_form": password_change_form,
    }, context_instance=RequestContext(request))
password_change = login_required(password_change)

def password_set(request, form_class=SetPasswordForm,
        template_name="account/password_set.html"):
    if request.user.password:
        return HttpResponseRedirect(reverse("acct_passwd"))
    if request.method == "POST":
        password_set_form = form_class(request.user, request.POST)
        if password_set_form.is_valid():
            password_set_form.save()
            return HttpResponseRedirect(reverse("acct_passwd"))
    else:
        password_set_form = form_class(request.user)
    return render_to_response(template_name, {
        "password_set_form": password_set_form,
    }, context_instance=RequestContext(request))
password_set = login_required(password_set)

def password_delete(request, template_name="account/password_delete.html"):
    # prevent this view when openids is not present or it is empty.
    if not request.user.password or (not hasattr(request, "openids") or not getattr(request, "openids", None)):
        return HttpResponseForbidden()
    if request.method == "POST":
        request.user.password = u""
        request.user.save()
        return HttpResponseRedirect(reverse("acct_passwd_delete_done"))
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))
password_delete = login_required(password_delete)

def password_reset(request, form_class=ResetPasswordForm,
        template_name="account/password_reset.html",
        template_name_done="account/password_reset_done.html"):
    if request.method == "POST":
        password_reset_form = form_class(request.POST)
        if password_reset_form.is_valid():
            email = password_reset_form.save()
            return render_to_response(template_name_done, {
                "email": email,
            }, context_instance=RequestContext(request))
    else:
        password_reset_form = form_class()
    
    return render_to_response(template_name, {
        "password_reset_form": password_reset_form,
    }, context_instance=RequestContext(request))

def timezone_change(request, form_class=ChangeTimezoneForm,
        template_name="account/timezone_change.html"):
    if request.method == "POST":
        form = form_class(request.user, request.POST)
        if form.is_valid():
            form.save()
    else:
        form = form_class(request.user)
    return render_to_response(template_name, {
        "form": form,
    }, context_instance=RequestContext(request))
timezone_change = login_required(timezone_change)

def language_change(request, form_class=ChangeLanguageForm,
        template_name="account/language_change.html"):
    if request.method == "POST":
        form = form_class(request.user, request.POST)
        if form.is_valid():
            form.save()
            next = request.META.get('HTTP_REFERER', None)
            return HttpResponseRedirect(next)
    else:
        form = form_class(request.user)
    return render_to_response(template_name, {
        "form": form,
    }, context_instance=RequestContext(request))
language_change = login_required(language_change)

def other_services(request, template_name="account/other_services.html"):
    from microblogging.utils import twitter_verify_credentials
    from microblogging.pownce_utils import pownce_verify_credentials
    twitter_form = TwitterForm(request.user)
    pownce_form = PownceForm(request.user)
    twitter_authorized = False
    pownce_authorized = False
    if request.method == "POST":
        twitter_form = TwitterForm(request.user, request.POST)

        if request.POST['actionType'] == 'saveTwitter':
            if twitter_form.is_valid():
                from microblogging.utils import twitter_account_raw
                twitter_account = twitter_account_raw(request.POST['username'], request.POST['password'])
                twitter_authorized = twitter_verify_credentials(twitter_account)
                if not twitter_authorized:
                    request.user.message_set.create(message="Twitter authentication failed")
                else:
                    twitter_form.save()
                
        if request.POST['actionType'] == 'savePownce':
            pownce_form = PownceForm(request.user, request.POST)     
            if pownce_form.is_valid():
                from microblogging.pownce_utils import pownce_account_raw
                pownce_account = pownce_account_raw(request.POST['usernamep'], request.POST['passwordp'])
                pownce_authorized = pownce_verify_credentials(pownce_account)
                if not pownce_authorized:
                    request.user.message_set.create(message="Pownce authentication failed")
                else:
                    pownce_form.save()
    else:
        from microblogging.utils import twitter_account_for_user
        from microblogging.pownce_utils import pownce_account_for_user
        twitter_account = twitter_account_for_user(request.user)
        pownce_account  = pownce_account_for_user(request.user)
        twitter_authorized = twitter_verify_credentials(twitter_account)
        pownce_authorized = pownce_verify_credentials(pownce_account)
        twitter_form = TwitterForm(request.user)
        pownce_form = PownceForm(request.user)
    return render_to_response(template_name, {
        "twitter_form": twitter_form,
        "twitter_authorized": twitter_authorized,
        "pownce_form": pownce_form,
        "pownce_authorized":pownce_authorized,
    }, context_instance=RequestContext(request))
other_services = login_required(other_services)
