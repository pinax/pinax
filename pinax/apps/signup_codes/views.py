from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login

from account.utils import get_default_redirect
from signup_codes.models import check_signup_code
from signup_codes.forms import SignupForm, InviteUserForm


def group_and_bridge(kwargs):
    """
    Given kwargs from the view (with view specific keys popped) pull out the
    bridge and fetch group from database.
    """
    
    bridge = kwargs.pop("bridge", None)
    
    if bridge:
        try:
            group = bridge.get_group(**kwargs)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None
    
    return group, bridge


def group_context(group, bridge):
    # @@@ use bridge
    return {
        "group": group,
    }


def signup(request, **kwargs):
    
    form_class = kwargs.pop("form_class", SignupForm)
    template_name = kwargs.pop("template_name", "account/signup.html")
    template_name_failure = kwargs.pop("template_name_failure", "signup_codes/failure.html")
    success_url = kwargs.pop("success_url", None)
    
    group, bridge = group_and_bridge(kwargs)
    ctx = group_context(group, context)
    
    if success_url is None:
        success_url = get_default_redirect(request)
    
    code = request.GET.get("code")
    
    if request.method == "POST":
        form = form_class(request.POST, group=group)
        if form.is_valid():
            username, password = form.save()
            user = authenticate(username=username, password=password)
            
            signup_code = form.cleaned_data["signup_code"]
            signup_code.use(user)
            
            auth_login(request, user)
            request.user.message_set.create(
                message = ugettext("Successfully logged in as %(username)s.") % {
                    "username": user.username,
            })
            return HttpResponseRedirect(success_url)
    else:
        signup_code = check_signup_code(code)
        if signup_code:
            form = form_class(initial={"signup_code": code}, group=group)
        else:
            if not settings.ACCOUNT_OPEN_SIGNUP:
                ctx.update({
                    "code": code,
                })
                ctx = RequestContext(request, ctx)
                # if account signup is not open we want to fail when there is
                # no sign up code or what was provided failed.
                return render_to_response(template_name_failure, ctx)
            else:
                form = form_class(group=group)
    
    ctx.update({
        "code": code,
        "form": form,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))


@staff_member_required
def admin_invite_user(request, **kwargs):
    """
    This view, by default, works inside the Django admin.
    """
    
    form_class = kwargs.pop("form_class", InviteUserForm)
    template_name = kwargs.pop("template_name", "signup_codes/admin_invite_user.html")
    
    group, bridge = group_and_bridge(kwargs)
    
    if request.method == "POST":
        form = form_class(request.POST, group=group)
        if form.is_valid():
            email = form.cleaned_data["email"]
            form.send_signup_code()
            request.user.message_set.create(message=ugettext("An e-mail has been sent to %(email)s.") % {"email": email})
            form = form_class() # reset
    else:
        form = form_class(group=group)
    
    ctx = group_context(group, context)
    ctx.update({
        "title": ugettext("Invite user"),
        "form": form,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))
