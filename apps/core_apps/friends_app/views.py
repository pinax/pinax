from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.conf import settings
from django.contrib.auth.decorators import login_required

from django.utils.translation import ugettext_lazy as _

from friends.models import *
from friends.forms import JoinRequestForm
from friends_app.forms import ImportVCardForm
from account.forms import SignupForm
from friends.importer import import_yahoo, import_google


# @@@ if made more generic these could be moved to django-friends proper

@login_required
def friends(request):
    if request.method == "POST":
        if request.POST["action"] == "accept":
            invitation_id = request.POST["invitation"]
            try:
                invitation = FriendshipInvitation.objects.get(id=invitation_id)
                if invitation.to_user == request.user:
                    invitation.accept()
                    request.user.message_set.create(message=_("Accepted friendship request from %(from_user)s") % {'from_user': invitation.from_user})
            except FriendshipInvitation.DoesNotExist:
                pass
            join_request_form = JoinRequestForm()
        elif request.POST["action"] == "invite": # invite to join
            join_request_form = JoinRequestForm(request.POST)
            if join_request_form.is_valid():
                join_request_form.save(request.user)
                join_request_form = JoinRequestForm() # @@@
    else:
        join_request_form = JoinRequestForm()
    
    invites_received = request.user.invitations_to.all().order_by("-sent")
    invites_sent = request.user.invitations_from.all().order_by("-sent")
    joins_sent = request.user.join_from.all().order_by("-sent")
    
    return render_to_response("friends_app/invitations.html", {
        "join_request_form": join_request_form,
        "invites_received": invites_received,
        "invites_sent": invites_sent,
        "joins_sent": joins_sent,
    }, context_instance=RequestContext(request))


def accept_join(request, confirmation_key):
    join_invitation = get_object_or_404(JoinInvitation, confirmation_key = confirmation_key.lower())
    if request.user.is_authenticated():
        return render_to_response("account/signup.html", {
            "contact_email": settings.CONTACT_EMAIL,
        }, context_instance=RequestContext(request))
    else:
        form = SignupForm(initial={"email": join_invitation.contact.email, "confirmation_key": join_invitation.confirmation_key })
        return render_to_response("account/signup.html", {
            "form": form,
            "contact_email": settings.CONTACT_EMAIL,
        }, context_instance=RequestContext(request))

@login_required
def contacts(request):
    if request.method == "POST":
        if request.POST["action"] == "upload_vcard":
            import_vcard_form = ImportVCardForm(request.POST, request.FILES)
            if import_vcard_form.is_valid():
                imported, total = import_vcard_form.save(request.user)
                request.user.message_set.create(message=_("%(total)s vCards found, %(imported)s contacts imported.") % {'imported': imported, 'total': total})
                import_vcard_form = ImportVCardForm()
        else:
            import_vcard_form = ImportVCardForm()
            if request.POST["action"] == "import_yahoo":
                bbauth_token = request.session.get('bbauth_token')
                del request.session['bbauth_token']
                if bbauth_token:
                    imported, total = import_yahoo(bbauth_token, request.user)
                    request.user.message_set.create(message=_("%(total)s people with email found, %(imported)s contacts imported.") % {'imported': imported, 'total': total})
            if request.POST["action"] == "import_google":
                authsub_token = request.session.get('authsub_token')
                del request.session['authsub_token']
                if authsub_token:
                    imported, total = import_google(authsub_token, request.user)
                    request.user.message_set.create(message=_("%(total)s people with email found, %(imported)s contacts imported.") % {'imported': imported, 'total': total})
    else:
        import_vcard_form = ImportVCardForm()
    
    return render_to_response("friends_app/contacts.html", {
        "import_vcard_form": import_vcard_form,
        "bbauth_token": request.session.get('bbauth_token'),
        "authsub_token": request.session.get('authsub_token'),
    }, context_instance=RequestContext(request))
