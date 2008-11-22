
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from django_openid.registration import RegistrationConsumer

from account.forms import OpenIDSignupForm

class PinaxConsumer(RegistrationConsumer):
    
    def on_registration_complete(self, request):
        return HttpResponseRedirect(reverse("what_next"))
    
    def show_i_have_logged_you_in(self, request):
        return HttpResponseRedirect(reverse("what_next"))
    
    def get_registration_form_class(self, request):
        return OpenIDSignupForm
    
    def render(self, request, template, context=None):
        # TODO: remove this method. this method is re-implemented to fix a
        # http://code.google.com/p/django-openid/issues/detail?id=22
        context = context or {}
        context['base_template'] = self.base_template
        return render_to_response(template, context,
            context_instance=RequestContext(request))