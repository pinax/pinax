from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from pinax.apps.waitinglist.forms import WaitingListEntryForm


def list_signup(request, post_save_redirect=None):
    if request.method == "POST":
        form = WaitingListEntryForm(request.POST)
        if form.is_valid():
            form.save()
            if post_save_redirect is None:
                post_save_redirect = reverse("waitinglist_success")
            if not post_save_redirect.startswith("/"):
                post_save_redirect = reverse(post_save_redirect)
            return HttpResponseRedirect(post_save_redirect)
    else:
        form = WaitingListEntryForm()
    context = {
        "form": form,
    }
    context = RequestContext(request, context)
    return render_to_response("waitinglist/list_signup.html", context)
