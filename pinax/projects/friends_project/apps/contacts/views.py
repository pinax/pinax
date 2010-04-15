from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.contrib.auth.decorators import login_required

from contacts_import.models import TransientContact

from contacts.models import Contact


@login_required
def contacts(request, template_name="contacts/contacts.html"):
    
    contacts = request.user.contacts.all()
    
    ctx = {
        "contacts": contacts,
    }
    
    return render_to_response(template_name, RequestContext(request, ctx))


def import_callback(request, selected):
    """
    This function is called by django-contacts-import (configured via
    CONTACTS_IMPORT_CALLBACK).
    """
    
    imported_contacts = TransientContact.objects.filter(pk__in=selected)
    
    for imported_contact in imported_contacts:
        contact = Contact(
            owner = request.user,
            name = imported_contact.name,
            email = imported_contact.email,
        )
        contact.save()
    
    return HttpResponseRedirect(reverse("contacts"))
