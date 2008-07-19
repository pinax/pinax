from django.conf import settings
from django import forms

from profiles.models import Profile

try:
    from notification import models as notification
except ImportError:
    notification = None

class ProfileForm(forms.ModelForm):
    
    class Meta:
        model = Profile
        exclude = ('user', 'timezone', 'language')
