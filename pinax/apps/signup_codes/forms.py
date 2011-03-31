from django import forms

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
        signup_code = SignupCode.create(email, 24, group=self.group)
        if commit:
            signup_code.save()
        return signup_code
    
    def send_signup_code(self):
        signup_code = self.create_signup_code()
        signup_code.send()
