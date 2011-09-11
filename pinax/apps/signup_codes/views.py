from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required

from pinax.apps.account.utils import get_default_redirect, user_display
from pinax.apps.signup_codes.models import SignupCode
from pinax.apps.signup_codes.forms import SignupForm, InviteUserForm


def group_and_bridge(request):
    """
    Given the request we can depend on the GroupMiddleware to provide the
    group and bridge.
    """
    
    # be group aware
    group = getattr(request, "group", None)
    if group:
        bridge = request.bridge
    else:
        bridge = None
    
    return group, bridge


def group_context(group, bridge):
    # @@@ use bridge
    ctx = {
        "group": group,
    }
    if group:
        ctx["group_base"] = bridge.group_base_template()
    return ctx


def signup(request, **kwargs):
    
    form_class = kwargs.pop("form_class", SignupForm)
    template_name = kwargs.pop("template_name", "account/signup.html")
    template_name_failure = kwargs.pop("template_name_failure", "signup_codes/failure.html")
    success_url = kwargs.pop("success_url", None)
    
    group, bridge = group_and_bridge(request)
    ctx = group_context(group, bridge)
    
    if success_url is None:
        if hasattr(settings, "SIGNUP_REDIRECT_URLNAME"):
            fallback_url = reverse(settings.SIGNUP_REDIRECT_URLNAME)
        else:
            if hasattr(settings, "LOGIN_REDIRECT_URLNAME"):
                fallback_url = reverse(settings.LOGIN_REDIRECT_URLNAME)
            else:
                fallback_url = settings.LOGIN_REDIRECT_URL
        success_url = get_default_redirect(request, fallback_url)
    
    code = request.GET.get("code")
    
    if request.method == "POST":
        form = form_class(request.POST, group=group)
        if form.is_valid():
            user = form.save(request=request)
            
            signup_code = form.cleaned_data["signup_code"]
            if signup_code:
                signup_code.use(user)
            
            form.login(request, user)
            messages.add_message(request, messages.SUCCESS,
                ugettext("Successfully logged in as %(username)s.") % {
                    "username": user_display(user),
                }
            )
            return HttpResponseRedirect(success_url)
    else:
        signup_code = SignupCode.check(code)
        if signup_code:
            initial = {
                "signup_code": code,
                "email": signup_code.email,
            }
            form = form_class(initial=initial, group=group)
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
    
    group, bridge = group_and_bridge(request)
    if request.method == "POST":
        form = form_class(request.POST, group=group)
        if form.is_valid():
            email = form.cleaned_data["email"]
            form.send_signup_code()
            messages.add_message(request, messages.INFO,
                ugettext("An email has been sent to %(email)s.") % {
                    "email": email
                }
            )
            form = form_class() # reset
    else:
        form = form_class(group=group)
    
    ctx = group_context(group, bridge)
    ctx.update({
        "title": ugettext("Invite user"),
        "form": form,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))
