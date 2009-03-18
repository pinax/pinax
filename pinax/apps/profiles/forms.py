from django import forms
from profiles.models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user', 'blogrss', 'timezone', 'language',
            'twitter_user', 'twitter_password')
