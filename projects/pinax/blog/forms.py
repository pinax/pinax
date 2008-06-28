from django import newforms as forms
from django.utils.translation import ugettext_lazy as _

from blog.models import Post

class BlogForm(forms.ModelForm):
    
    slug = forms.RegexField(max_length=20, regex=r'^\w+$',
        help_text = _("a short version of the name consisting only of letters, numbers and underscores."),
        error_message = _("This value must contain only letters, numbers and underscores."))
    
    class Meta:
        model = Post
        exclude = ('author', 'creator_ip', 'created_at', 'updated_at', 'publish')
