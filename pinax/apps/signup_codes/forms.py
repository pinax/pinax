from datetime import datetime, timedelta

from django import forms
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor
from django.utils.translation import ugettext_lazy as _, ugettext

from django.contrib.sites.models import Site

from pinax.core.utils import get_send_mail
send_mail = get_send_mail()

from pinax.apps.account.forms import GroupForm, SignupForm as BaseSignupForm
from pinax.apps.signup_codes.models import SignupCode, check_signup_code


class SignupForm(BaseSignupForm):
    
    signup_code = forms.CharField(max_length=40, required=False, widget=forms.HiddenInput())
    
    def clean_signup_code(self):
        code = self.cleaned_data.get("signup_code")
        signup_code = check_signup_code(code)
        if signup_code:
            return signup_code
        else:
            raise forms.ValidationError("Signup code was not valid.")


class InviteUserForm(GroupForm):
    
    email = forms.EmailField()
    
    def create_signup_code(self, commit=True):
        email = self.cleaned_data["email"]
        expiry = datetime.now() + timedelta(hours=1)
        bits = [
            settings.SECRET_KEY,
            email,
            str(expiry),
        ]
        if self.group:
            bits.append("%s%s" % (self.group._meta, self.group.pk))
        code = sha_constructor("".join(bits)).hexdigest()
        signup_code = SignupCode(code=code, email=email, max_uses=1, expiry=expiry)
        if commit:
            signup_code.save()
        return signup_code
    
    def send_signup_code(self):
        email = self.cleaned_data["email"]
        signup_code = self.create_signup_code()
        
        current_site = Site.objects.get_current()
        domain = unicode(current_site.domain)
        
        ctx = {
            "group": self.group,
            "signup_code": signup_code,
            "domain": domain,
        }
        subject = render_to_string("signup_codes/invite_user_subject.txt", ctx)
        message = render_to_string("signup_codes/invite_user.txt", ctx)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], priority="high")
