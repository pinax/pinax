from django.shortcuts import render_to_response
from django.template import RequestContext

from django.contrib.auth.decorators import login_required


@login_required
def contacts(request, template_name="contacts/contacts.html"):
    
    contacts = request.user.contacts.all()
    
    ctx = {
        "contacts": contacts,
    }
    
    return render_to_response(template_name, RequestContext(request, ctx))


def import_callback(request, selected):
    pass
