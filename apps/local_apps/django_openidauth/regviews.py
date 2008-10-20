
import re

from django import forms
from django.contrib.auth import login as log_user_in, load_backend
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.models import User
from emailconfirmation.models import EmailAddress

from django_openidauth.models import associate_openid

alnum_re = re.compile(r'^\w+$')

class RegistrationFormOpenID(forms.Form):
    username = forms.CharField(label="Username", max_length=30, widget=forms.TextInput())
    email = forms.EmailField(label="Email (optional)", required=False, widget=forms.TextInput())

    def clean_username(self):
        if not alnum_re.search(self.cleaned_data["username"]):
            raise forms.ValidationError(u"Usernames can only contain letters, numbers and underscores.")
        try:
            user = User.objects.get(username__exact=self.cleaned_data["username"])
        except User.DoesNotExist:
            return self.cleaned_data["username"]
        raise forms.ValidationError(u"This username is already taken. Please choose another.")

    def save(self):
        username = self.cleaned_data["username"]
        email = self.cleaned_data["email"]
        new_user = User.objects.create_user(username, "", "!")
        
        if email:
            new_user.message_set.create(message="Confirmation email sent to %s" % email)
            EmailAddress.objects.add_email(new_user, email)
        return new_user

def register(request, success_url='/accounts/register/complete/',
        template_name='openid_register.html', already_registered_url='/'):
    """
    Allows a new user to register an account. A customised variation of the
    view of the same name from django-registration.

    Context::
        form
            The registration form

    Template::
        registration/registration_form.html (or template_name argument)

    """
    if request.method == 'POST':
        form = RegistrationFormOpenID(request.POST)

        if form.is_valid():
            new_user = form.save()
            associate_openid( new_user, request.openid )

            # Unfortunately we have to annotate the user with the
            # 'django.contrib.auth.backends.ModelBackend' backend, or stuff breaks
            backend = load_backend('django.contrib.auth.backends.ModelBackend')
            new_user.backend = '%s.%s' % (
                backend.__module__, backend.__class__.__name__
            )
            log_user_in(request, new_user)

            return HttpResponseRedirect(success_url)
    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect( already_registered_url )
        form = RegistrationFormOpenID()

    return render_to_response(template_name, { 'form': form },
                              context_instance=RequestContext(request))
