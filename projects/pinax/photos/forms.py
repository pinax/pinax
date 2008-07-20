from django import forms
from datetime import datetime
from django.utils.translation import ugettext_lazy as _

from photos.models import Photos

class PhotoUploadForm(forms.ModelForm):
    
    class Meta:
        model = Photos
        exclude = ('member','photoset','title_slug','effect','crop_from')
        
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(PhotoUploadForm, self).__init__(*args, **kwargs)