from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


def yahoo_callback(request, access, token):
    request.session["%s_token" % access.service] = str(token)
    return HttpResponseRedirect(reverse("import_contacts"))