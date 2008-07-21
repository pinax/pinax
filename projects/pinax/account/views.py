
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.template import RequestContext
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from forms import SignupForm, AddEmailForm, LoginForm, ChangePasswordForm, ResetPasswordForm, ChangeTimezoneForm, ChangeLanguageForm, TwitterForm
from emailconfirmation.models import EmailAddress, EmailConfirmation
from friends.models import Friendship
from profiles.models import Profile


def login(request):
    redirect_to = request.REQUEST.get("next", reverse("what_next"))
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.login(request):
            return HttpResponseRedirect(redirect_to)
    else:
        form = LoginForm()
    return render_to_response("account/login.html", {
        "form": form,
    }, context_instance=RequestContext(request))

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            username, password = form.save()
            user = authenticate(username=username, password=password)
            auth_login(request, user)
            request.user.message_set.create(message=_("Successfully logged in as %(username)s.") % {'username': user.username})
            return HttpResponseRedirect(reverse("what_next"))
    else:
        form = SignupForm()
    return render_to_response("account/signup.html", {
        "form": form,
    }, context_instance=RequestContext(request))

@login_required
def email(request):
    if request.method == "POST" and request.user.is_authenticated():
        if request.POST["action"] == "add":
            add_email_form = AddEmailForm(request.user, request.POST)
            if add_email_form.is_valid():
                add_email_form.save()
                add_email_form = AddEmailForm() # @@@
        else:
            add_email_form = AddEmailForm()
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
        add_email_form = AddEmailForm()
    
    return render_to_response("account/email.html", {
        "add_email_form": add_email_form,
    }, context_instance=RequestContext(request))

@login_required
def password_change(request):
    if request.method == "POST":
        password_change_form = ChangePasswordForm(request.user, request.POST)
        if password_change_form.is_valid():
            password_change_form.save()
            password_change_form = ChangePasswordForm(request.user)
    else:
        password_change_form = ChangePasswordForm(request.user)
    return render_to_response("account/password_change.html", {
        "password_change_form": password_change_form,
    }, context_instance=RequestContext(request))
password_change = login_required(password_change)

def password_reset(request):
    if request.method == "POST":
        password_reset_form = ResetPasswordForm(request.POST)
        if password_reset_form.is_valid():
            email = password_reset_form.save()
            return render_to_response("account/password_reset_done.html", {
                "email": email,
            }, context_instance=RequestContext(request))
    else:
        password_reset_form = ResetPasswordForm()
    
    return render_to_response("account/password_reset.html", {
        "password_reset_form": password_reset_form,
    }, context_instance=RequestContext(request))

@login_required
def timezone_change(request):
    if request.method == "POST":
        form = ChangeTimezoneForm(request.user, request.POST)
        if form.is_valid():
            form.save()
    else:
        form = ChangeTimezoneForm(request.user)
    return render_to_response("account/timezone_change.html", {
        "form": form,
    }, context_instance=RequestContext(request))

@login_required
def language_change(request):
    if request.method == "POST":
        form = ChangeLanguageForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            next = request.META.get('HTTP_REFERER', None)
            return HttpResponseRedirect(next)
    else:
        form = ChangeLanguageForm(request.user)
    return render_to_response("account/language_change.html", {
        "form": form,
    }, context_instance=RequestContext(request))

from gravatar.templatetags.gravatar import gravatar

@login_required
def other_services(request):
    from zwitschern.utils import twitter_verify_credentials
    twitter_form = TwitterForm(request.user)
    twitter_authorized = False
    if request.method == "POST":
        twitter_form = TwitterForm(request.user, request.POST)
        if twitter_form.is_valid():
            from zwitschern.utils import twitter_account_raw
            twitter_account = twitter_account_raw(request.POST['username'], request.POST['password'])
            twitter_authorized = twitter_verify_credentials(twitter_account)
            if not twitter_authorized:
                request.user.message_set.create(message="Twitter authentication failed")
            else:
                twitter_form.save()
    else:
        from zwitschern.utils import twitter_account_for_user
        twitter_account = twitter_account_for_user(request.user)
        twitter_authorized = twitter_verify_credentials(twitter_account)
        twitter_form = TwitterForm(request.user)
    return render_to_response("account/other_services.html", {
        "twitter_form": twitter_form,
        "twitter_authorized": twitter_authorized,
    }, context_instance=RequestContext(request))    

def username_autocomplete(request):
    if request.user.is_authenticated():
        q = request.GET.get("q")
        friends = Friendship.objects.friends_for_user(request.user)
        content = []
        for friendship in friends:
            if friendship["friend"].username.lower().startswith(q):
                try:
                    profile = friendship["friend"].get_profile()
                    entry = "%s,,%s,,%s" % (
                        gravatar(friendship["friend"], 40),
                        friendship["friend"].username,
                        profile.location
                    )
                except Profile.DoesNotExist:
                    pass
                content.append(entry)
        response = HttpResponse("\n".join(content))
    else:
        response = HttpResponseForbidden()
    setattr(response, "djangologging.suppress_output", True)
    return response
