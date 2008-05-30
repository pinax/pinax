from django import newforms as forms
from django.utils.translation import ugettext_lazy as _

from tribes.models import *

class TribeForm(forms.ModelForm):
    
    slug = forms.RegexField(max_length=20, regex=r'^\w+$',
        help_text = _("a short version of the name consisting only of letters, numbers and underscores."),
        error_message = _("This value must contain only letters, numbers and underscores."))
            
    def clean_slug(self):
        if Tribe.objects.filter(slug=self.cleaned_data["slug"]).count() > 0:
            raise forms.ValidationError(_("A tribe already exists with that slug."))
        return self.cleaned_data["slug"]
    
    def clean_name(self):
        if Tribe.objects.filter(name=self.cleaned_data["name"]).count() > 0:
            raise forms.ValidationError(_("A tribe already exists with that name."))
        return self.cleaned_data["name"]
    
    class Meta:
        model = Tribe
        fields = ('name', 'slug', 'description')


# @@@ is this the right approach, to have two forms where creation and update fields differ?

class TribeUpdateForm(forms.ModelForm):
    
    def clean_name(self):
        if Tribe.objects.filter(name=self.cleaned_data["name"]).count() > 0:
            raise forms.ValidationError(_("A tribe already exists with that name."))
        return self.cleaned_data["name"]
    
    class Meta:
        model = Tribe
        fields = ('name', 'description')


class TopicForm(forms.ModelForm):
    
    class Meta:
        model = Topic
        fields = ('title', 'body')