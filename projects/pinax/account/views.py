from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.template import RequestContext
from django.conf import settings

from forms import SignupForm, AddEmailForm, LoginForm, ChangePasswordForm, ResetPasswordForm
from emailconfirmation.models import EmailAddress, EmailConfirmation

def login(request):
    redirect_to = request.REQUEST.get("next", "/account/")
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
            request.user.message_set.create(message="Successfully logged in as %s." % user.username)
            return HttpResponseRedirect("/")
    else:
        form = SignupForm()
    return render_to_response("account/signup.html", {
        "form": form,
    }, context_instance=RequestContext(request))

def account(request):
    if request.method == "POST" and request.user.is_authenticated():
        if request.POST["action"] == "add":
            password_change_form = ChangePasswordForm(request.user)
            add_email_form = AddEmailForm(request.user, request.POST)
            if add_email_form.is_valid():
                add_email_form.save()
                add_email_form = AddEmailForm() # @@@
        else:
            add_email_form = AddEmailForm()
            if request.POST["action"] == "change password":
                password_change_form = ChangePasswordForm(request.user, request.POST)
                if password_change_form.is_valid():
                    password_change_form.save()
                    password_change_form = ChangePasswordForm(request.user)
            else:
                password_change_form = ChangePasswordForm(request.user)
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
        password_change_form = ChangePasswordForm(request.user)
    
    return render_to_response("account/account.html", {
        "add_email_form": add_email_form,
        "password_change_form": password_change_form,
    }, context_instance=RequestContext(request))

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
