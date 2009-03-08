
from django import forms

from account.forms import SignupForm as BaseSignupForm
from signup_codes.models import check_signup_code

class SignupForm(BaseSignupForm):
    signup_code = forms.CharField(max_length=40, required=False, widget=forms.HiddenInput())
    
    def clean_signup_code(self):
        code = self.cleaned_data.get("signup_code")
        signup_code = check_signup_code(code)
        if signup_code:
            return signup_code
        else:
            raise forms.ValidationError("Signup code was not valid.")
