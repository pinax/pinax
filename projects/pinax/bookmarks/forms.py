from django import newforms as forms
from django.utils.translation import ugettext_lazy as _

from bookmarks.models import Bookmark

class BookmarkForm(forms.ModelForm):
    
    url = forms.URLField(label = "URL", verify_exists=True, widget=forms.TextInput(attrs={"size": 40}))
    description = forms.CharField(widget=forms.TextInput(attrs={"size": 40}))
    
    def clean_url(self):
        if Bookmark.objects.filter(url=self.cleaned_data["url"]).count() > 0:
            raise forms.ValidationError(_("That url has already been submitted and Pinax does not yet support multiple bookmarking of a URL"))
        return self.cleaned_data["name"]
    
    class Meta:
        model = Bookmark
        exclude = ('adder', 'added',)