from django import newforms as forms

from profiles.models import Profile

try:
    from notification import models as notification
except ImportError:
    notification = None

class ProfileForm(forms.ModelForm):
    
    class Meta:
        model = Profile
        exclude = ('user')