from django import forms
from django.utils.translation import ugettext_lazy as _

from tribes.models import Tribe, Topic

class TribeForm(forms.ModelForm):
    
    slug = forms.SlugField(max_length=20,
        help_text = _("a short version of the name consisting only of letters, numbers, underscores and hyphens."),
        error_message = _("This value must contain only letters, numbers, underscores and hyphens."))
            
    def clean_slug(self):
        reserved_slugs = ["your_tribes"]
        if self.cleaned_data["slug"] in reserved_slugs:
            raise forms.ValidationError(_("The slug you've chosen is reserved for internal use."))
        if Tribe.objects.filter(slug__iexact=self.cleaned_data["slug"]).count() > 0:
            raise forms.ValidationError(_("A tribe already exists with that slug."))
        return self.cleaned_data["slug"].lower()
    
    def clean_name(self):
        if Tribe.objects.filter(name__iexact=self.cleaned_data["name"]).count() > 0:
            raise forms.ValidationError(_("A tribe already exists with that name."))
        return self.cleaned_data["name"]
    
    class Meta:
        model = Tribe
        fields = ('name', 'slug', 'description', 'tags')


# @@@ is this the right approach, to have two forms where creation and update fields differ?

class TribeUpdateForm(forms.ModelForm):
    
    def clean_name(self):
        if Tribe.objects.filter(name__iexact=self.cleaned_data["name"]).count() > 0:
            if self.cleaned_data["name"] == self.instance.name:
                pass # same instance
            else:
                raise forms.ValidationError(_("A tribe already exists with that name."))
        return self.cleaned_data["name"]
    
    class Meta:
        model = Tribe
        fields = ('name', 'description', 'tags')


class TopicForm(forms.ModelForm):
    
    class Meta:
        model = Topic
        fields = ('title', 'body', 'tags')
