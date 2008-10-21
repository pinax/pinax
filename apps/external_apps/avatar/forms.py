from django import forms
from django.forms import widgets
from django.utils.safestring import mark_safe

def avatar_img(avatar, size):
    if not avatar.thumbnail_exists(size):
        avatar.create_thumbnail(size)
    return mark_safe("""<img src="%s" alt="%s" />""" % 
        (avatar.avatar_url(size), unicode(avatar)))

class PrimaryAvatarForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        size = kwargs.pop('size', 80)
        super(PrimaryAvatarForm, self).__init__(*args, **kwargs)
        avatars = user.avatar_set.all()
        self.fields['choice'] = forms.ChoiceField(
            choices=[(c.id, avatar_img(c, size)) for c in user.avatar_set.all()],
            widget=widgets.RadioSelect)

class DeleteAvatarForm(forms.Form):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        size = kwargs.pop('size', 80)
        super(DeleteAvatarForm, self).__init__(*args, **kwargs)
        avatars = user.avatar_set.all()
        self.fields['choices'] = forms.MultipleChoiceField(
            choices=[(c.id, avatar_img(c, size)) for c in user.avatar_set.all()],
            widget=widgets.CheckboxSelectMultiple)
