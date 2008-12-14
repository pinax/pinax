from datetime import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User
try:
    from notification import models as notification
except ImportError:
    notification = None

from projects.models import Project, Topic, Task, ProjectMember

# @@@ this is based on Tribes -- can we re-use anything?

class ProjectForm(forms.ModelForm):
    
    slug = forms.SlugField(max_length=20,
        help_text = _("a short version of the name consisting only of letters, numbers, underscores or hyphens."),
        error_message = _("This value must contain only letters, numbers, underscores and hyphens."))
            
    def clean_slug(self):
        if Project.objects.filter(slug__iexact=self.cleaned_data["slug"]).count() > 0:
            raise forms.ValidationError(_("A project already exists with that slug."))
        return self.cleaned_data["slug"].lower()
    
    def clean_name(self):
        if Project.objects.filter(name__iexact=self.cleaned_data["name"]).count() > 0:
            raise forms.ValidationError(_("A project already exists with that name."))
        return self.cleaned_data["name"]
    
    class Meta:
        model = Project
        fields = ('name', 'slug', 'description', 'tags')


# @@@ is this the right approach, to have two forms where creation and update fields differ?

class ProjectUpdateForm(forms.ModelForm):
    
    def clean_name(self):
        if Project.objects.filter(name__iexact=self.cleaned_data["name"]).count() > 0:
            if self.cleaned_data["name"] == self.instance.name:
                pass # same instance
            else:
                raise forms.ValidationError(_("A project already exists with that name."))
        return self.cleaned_data["name"]
    
    class Meta:
        model = Project
        fields = ('name', 'description', 'tags')

class TopicForm(forms.ModelForm):
    
    class Meta:
        model = Topic
        fields = ('title', 'body', 'tags')


class TaskForm(forms.ModelForm):
    def __init__(self, project, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields["assignee"].queryset = self.fields["assignee"].queryset.filter(project=project)
    
    class Meta:
        model = Task
        fields = ('summary', 'detail', 'assignee', 'tags')


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
    
    def __init__(self, project, *args, **kwargs):
        super(AddUserForm, self).__init__(*args, **kwargs)
        self.project = project
    
    def clean_recipient(self):
        try:
            user = User.objects.get(username__exact=self.cleaned_data['recipient'])
        except User.DoesNotExist:
            raise forms.ValidationError(_("There is no user with this username."))
            
        if ProjectMember.objects.filter(project=self.project, user=user).count() > 0:
            raise forms.ValidationError(_("User is already a member of this project."))
        
        return self.cleaned_data['recipient']
    
    # @@@ we don't need to pass in project any more as we have self.project
    def save(self, project, user):
        new_member = User.objects.get(username__exact=self.cleaned_data['recipient'])
        project_member = ProjectMember(project=project, user=new_member)
        project_member.save()
        project.members.add(project_member)
        if notification:
            notification.send(project.member_users.all(), "projects_new_member", {"new_member": new_member, "project": project})
            notification.send([new_member], "projects_added_as_member", {"adder": user, "project": project})
        user.message_set.create(message="added %s to project" % new_member)


class AwayForm(forms.Form):
    
    away_message = forms.CharField(label=_(u"Message"))
    
    def save(self, project_member):
        project_member.away = True
        project_member.away_message = self.cleaned_data['away_message']
        project_member.away_since = datetime.now()
        project_member.save()

