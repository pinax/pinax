from django.conf import settings
from django import forms

from basic_profiles.models import Profile

class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        exclude = ('user',)
