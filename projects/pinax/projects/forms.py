from django import newforms as forms
from django.utils.translation import ugettext_lazy as _

from projects.models import *

# @@@ this is based on Tribes -- can we re-use anything?

class ProjectForm(forms.ModelForm):
    
    slug = forms.RegexField(max_length=20, regex=r'^\w+$',
        help_text = _("a short version of the name consisting only of letters, numbers and underscores."),
        error_message = _("This value must contain only letters, numbers and underscores."))
            
    def clean_slug(self):
        if Project.objects.filter(slug=self.cleaned_data["slug"]).count() > 0:
            raise forms.ValidationError(_("A project already exists with that slug."))
        return self.cleaned_data["slug"]
    
    def clean_name(self):
        if Project.objects.filter(name=self.cleaned_data["name"]).count() > 0:
            raise forms.ValidationError(_("A project already exists with that name."))
        return self.cleaned_data["name"]
    
    class Meta:
        model = Project
        fields = ('name', 'slug', 'description')


# @@@ is this the right approach, to have two forms where creation and update fields differ?

class ProjectUpdateForm(forms.ModelForm):
    
    def clean_name(self):
        if Project.objects.filter(name=self.cleaned_data["name"]).count() > 0:
            if self.cleaned_data["name"] == self.instance.name:
                pass # same instance
            else:
                raise forms.ValidationError(_("A project already exists with that name."))
        return self.cleaned_data["name"]
    
    class Meta:
        model = Project
        fields = ('name', 'description')

class TopicForm(forms.ModelForm):
    
    class Meta:
        model = Topic
        fields = ('title', 'body')


class TaskForm(forms.ModelForm):
    def __init__(self, project, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields["assignee"].queryset = self.fields["assignee"].queryset.filter(project=project)
    
    class Meta:
        model = Task
        fields = ('summary', 'detail', 'assignee')


class AssignForm(TaskForm):
    """
    a form for changing the assignee of a task
    """
    class Meta(TaskForm.Meta):
        fields = ('assignee',)


class StatusForm(forms.ModelForm):
    """
    a form for changing the status of a task
    """
    status = forms.CharField(widget=forms.TextInput(attrs={'size':'40'}))
    
    class Meta:
        model = Task
        fields = ('status',)


class AddUserForm(forms.Form):
    
    recipient = forms.CharField(label=_(u"User"))
    
    def clean_recipient(self):
        # @@@ really should also check if already a member
        try:
            User.objects.get(username__exact=self.cleaned_data['recipient'])
        except User.DoesNotExist:
            raise forms.ValidationError(_("There is no user with this username."))
        return self.cleaned_data['recipient']
    
    def save(self, project, user):
        new_member = User.objects.get(username__exact=self.cleaned_data['recipient'])
        project.members.add(new_member)
        if notification:
            notification.send(project.members.all(), "projects_new_member", "%(new_member)s has been added to project %(project)s.", {"new_member": new_member, "project": project})
            notification.send([new_member], "projects_added_as_member", "you have been added to project %(project)s by %(adder)s.", {"adder": user, "project": project})
        user.message_set.create(message="added %s to project" % new_member)
