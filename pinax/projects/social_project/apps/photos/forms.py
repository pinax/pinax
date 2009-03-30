from django import forms
from datetime import datetime
from django.utils.translation import ugettext_lazy as _

from photos.models import Image

class PhotoUploadForm(forms.ModelForm):
    
    class Meta:
        model = Image
        exclude = ('member','photoset','title_slug','effect','crop_from')
        
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(PhotoUploadForm, self).__init__(*args, **kwargs)

class PhotoEditForm(forms.ModelForm):
    
    class Meta:
        model = Image
        exclude = ('member','photoset','title_slug','effect','crop_from','image')
        
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(PhotoEditForm, self).__init__(*args, **kwargs)
