from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.utils.translation import ugettext

from django.contrib.admin.views.decorators import staff_member_required

from account.utils import get_default_redirect
from signup_codes.models import check_signup_code
from signup_codes.forms import SignupForm, InviteUserForm


def signup(request, form_class=SignupForm,
        template_name="account/signup.html", success_url=None):
    if success_url is None:
        success_url = get_default_redirect(request)
    
    code = request.GET.get("code")
    
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            username, password = form.save()
            user = authenticate(username=username, password=password)
            
            signup_code = form.cleaned_data["signup_code"]
            signup_code.use(user)
            
            auth_login(request, user)
            request.user.message_set.create(
                message=ugettext("Successfully logged in as %(username)s.") % {
                'username': user.username
            })
            return HttpResponseRedirect(success_url)
    else:
        signup_code = check_signup_code(code)
        if signup_code:
            form = form_class(initial={"signup_code": code})
        else:
            if not settings.ACCOUNT_OPEN_SIGNUP:
                # if account signup is not open we want to fail when there is
                # no sign up code or what was provided failed.
                return render_to_response("signup_codes/failure.html", {
                    "code": code,
                }, context_instance=RequestContext(request))
            else:
                form = form_class()
    return render_to_response(template_name, {
        "code": code,
        "form": form,
    }, context_instance=RequestContext(request))


@staff_member_required
def admin_invite_user(request, form_class=InviteUserForm,
        template_name="signup_codes/admin_invite_user.html"):
    """
    This view, by default, works inside the Django admin.
    """
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            form.send_signup_code()
            request.user.message_set.create(message=ugettext("An e-mail has been sent to %(email)s.") % {"email": email})
            form = form_class() # reset
    else:
        form = form_class()
    return render_to_response(template_name, {
        "title": ugettext("Invite user"),
        "form": form,
    }, context_instance=RequestContext(request))
