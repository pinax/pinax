from django import forms
from django.contrib.auth.models import User

from friends.models import *
from friends.importer import import_vcards

# @@@ move to django-friends when ready

class ImportVCardForm(forms.Form):
    
    vcard_file = forms.FileField(label="vCard File")
    
    def save(self, user):
        imported, total = import_vcards(self.cleaned_data["vcard_file"].content, user)
        return imported, total
        
