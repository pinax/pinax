
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from django_openid.registration import RegistrationConsumer

from account.forms import OpenIDSignupForm

class PinaxConsumer(RegistrationConsumer):
    
    def on_registration_complete(self, request):
        return HttpResponseRedirect(reverse("what_next"))
    
    def show_i_have_logged_you_in(self, request):
        return HttpResponseRedirect(reverse("what_next"))
    
    def get_registration_form_class(self, request):
        return OpenIDSignupForm