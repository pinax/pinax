
from account.forms import SignupForm

def signup(request, form_class=SignupForm,
        template_name="account/signup.html", success_url=None):
    if success_url is None:
        success_url = get_default_redirect(request)
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            username, password = form.save()
            user = authenticate(username=username, password=password)
            auth_login(request, user)
            request.user.message_set.create(
                message=_("Successfully logged in as %(username)s.") % {
                'username': user.username
            })
            return HttpResponseRedirect(success_url)
    else:
        code = request.GET.get("code")
        signup_code = check_signup_code(code)
        if signup_code:
            form = form_class(initial={"signup_code": code})
        else:
            if not settings.ACCOUNT_OPEN_SIGNUP:
                # if account signup is not open we want to fail when there is
                # no sign up code or what was provided failed.
                return render_to_reponse("signup_code/failure.html", {
                    "code": code,
                }, context_instance=RequestContext(request))
            else:
                form = form_class()
    return render_to_response(template_name, {
        "form": form,
    }, context_instance=RequestContext(request))
