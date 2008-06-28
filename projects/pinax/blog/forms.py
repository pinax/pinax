from django import newforms as forms
from django.newforms import widgets
from django.utils.translation import ugettext_lazy as _

from blog.models import Post

class BlogForm(forms.ModelForm):
	
	class Meta:
		model = Post
		exclude = ('author', 'creator_ip',
                   'created_at', 'updated_at', 'publish')
