from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.utils.translation import ugettext, ugettext_lazy as _

from friends.forms import JoinRequestForm
from friends.importer import import_yahoo, import_google
from friends.models import *

from pinax.apps.account.forms import SignupForm

from friends_app.forms import ImportVCardForm



# @@@ if made more generic these could be moved to django-friends proper

@login_required
def friends(request, template_name="friends_app/invitations.html"):
    if request.method == "POST":
        invitation_id = request.POST.get("invitation", None)
        if request.POST["action"] == "accept":
            try:
                invitation = FriendshipInvitation.objects.get(id=invitation_id)
                if invitation.to_user == request.user:
                    invitation.accept()
                    messages.add_message(request, messages.SUCCESS,
                        ugettext("Accepted friendship request from %(from_user)s") % {
                            "from_user": invitation.from_user
                        }
                    )
            except FriendshipInvitation.DoesNotExist:
                pass
        elif request.POST["action"] == "decline":
            try:
                invitation = FriendshipInvitation.objects.get(id=invitation_id)
                if invitation.to_user == request.user:
                    invitation.decline()
                    messages.add_message(request, messages.SUCCESS,
                        ugettext("Declined friendship request from %(from_user)s") % {
                            "from_user": invitation.from_user
                        }
                    )
            except FriendshipInvitation.DoesNotExist:
                pass
    
    invites_received = request.user.invitations_to.invitations().order_by("-sent")
    invites_sent = request.user.invitations_from.invitations().order_by("-sent")
    joins_sent = request.user.join_from.all().order_by("-sent")
    
    return render_to_response(template_name, {
        "invites_received": invites_received,
        "invites_sent": invites_sent,
        "joins_sent": joins_sent,
    }, context_instance=RequestContext(request))


@login_required
def invite(request, form_class=JoinRequestForm, **kwargs):
    template_name = kwargs.get("template_name", "friends_app/invite.html")
    if request.is_ajax():
        template_name = kwargs.get(
            "template_name_facebox",
            "friends_app/invite_facebox.html"
        )
    
    join_request_form = form_class()
    if request.method == "POST":
        join_request_form = form_class(request.POST)
        if join_request_form.is_valid():
            join_request_form.save(request.user)
            return HttpResponseRedirect(reverse("invitations"))
    return render_to_response(template_name, {
        "join_request_form": join_request_form,
        }, context_instance=RequestContext(request))


def accept_join(request, confirmation_key, form_class=SignupForm,
        template_name="account/signup.html"):
    join_invitation = get_object_or_404(JoinInvitation, confirmation_key=confirmation_key.lower())
    if request.user.is_authenticated():
        return render_to_response("account/signup.html", {
        }, context_instance=RequestContext(request))
    else:
        form = form_class(initial={
            "email": join_invitation.contact.email,
            "confirmation_key": join_invitation.confirmation_key
        })
        return render_to_response(template_name, {
            "form": form,
        }, context_instance=RequestContext(request))


@login_required
def contacts(request, form_class=ImportVCardForm,
        template_name="friends_app/contacts.html"):
    if request.method == "POST":
        if request.POST["action"] == "upload_vcard":
            import_vcard_form = form_class(request.POST, request.FILES)
            if import_vcard_form.is_valid():
                imported, total = import_vcard_form.save(request.user)
                messages.add_message(request, messages.SUCCESS,
                    ugettext("%(total)s vCards found, %(imported)s contacts imported.") % {
                        "imported": imported,
                        "total": total
                    }
                )
                import_vcard_form = ImportVCardForm()
        else:
            import_vcard_form = form_class()
            if request.POST["action"] == "import_yahoo":
                bbauth_token = request.session.get("bbauth_token")
                del request.session["bbauth_token"]
                if bbauth_token:
                    imported, total = import_yahoo(bbauth_token, request.user)
                    messages.add_message(request, message.SUCCESS,
                        ugettext("%(total)s people with email found, %(imported)s contacts imported.") % {
                            "imported": imported,
                            "total": total
                        }
                    )
            if request.POST["action"] == "import_google":
                authsub_token = request.session.get("authsub_token")
                del request.session["authsub_token"]
                if authsub_token:
                    imported, total = import_google(authsub_token, request.user)
                    messages.add_message(request, messages.SUCCESS,
                        ugettext("%(total)s people with email found, %(imported)s contacts imported.") % {
                            "imported": imported,
                            "total": total
                        }
                    )
    else:
        import_vcard_form = form_class()
    
    return render_to_response(template_name, {
        "import_vcard_form": import_vcard_form,
        "bbauth_token": request.session.get("bbauth_token"),
        "authsub_token": request.session.get("authsub_token"),
    }, context_instance=RequestContext(request))


@login_required
def friends_objects(request, template_name, friends_objects_function, extra_context={}):
    """
    Display friends' objects.
    
    This view takes a template name and a function. The function should
    take an iterator over users and return an iterator over objects
    belonging to those users. This iterator over objects is then passed
    to the template of the given name as ``object_list``.
    
    The template is also passed variable defined in ``extra_context``
    which should be a dictionary of variable names to functions taking a
    request object and returning the value for that variable.
    """
    
    friends = friend_set_for(request.user)
    
    dictionary = {
        "object_list": friends_objects_function(friends),
    }
    for name, func in extra_context.items():
        dictionary[name] = func(request)
    
    return render_to_response(template_name, dictionary, context_instance=RequestContext(request))
