from datetime import datetime
from sys import stderr

from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_app
from django.utils.translation import ugettext

from django.contrib.auth.models import User

from pinax.apps.tasks.models import Task, TaskHistory, workflow
from pinax.apps.tasks.widgets import ReadOnlyWidget

from pinax.apps.tagging_utils.widgets import TagAutoCompleteInput
from tagging.forms import TagField



class TaskForm(forms.ModelForm):
    """
    Form for creating tasks
    """
    
    tags = TagField(
        required = False,
        widget = TagAutoCompleteInput(app_label="tasks", model="task")
    )
    
    def __init__(self, user, group, *args, **kwargs):
        self.user = user
        self.group = group
        
        super(TaskForm, self).__init__(*args, **kwargs)
        
        if group:
            assignee_queryset = group.member_queryset()
        else:
            assignee_queryset = self.fields["assignee"].queryset
        
        self.fields["assignee"].queryset = assignee_queryset.order_by("username")
        self.fields["summary"].widget.attrs["size"] = 65
    
    class Meta:
        model = Task
        fields = ["summary", "detail", "assignee", "tags", "markup"]
    
    def clean(self):
        self.check_group_membership()
        return self.cleaned_data
    
    def check_group_membership(self):
        group = self.group
        if group and not self.group.user_is_member(self.user):
            raise forms.ValidationError("You must be a member to create tasks")


class EditTaskForm(forms.ModelForm):
    """
    Form for editing tasks
    """
    
    status = forms.CharField(
        required = False,
        widget = forms.TextInput(attrs={"size": "50", "maxlength": "100"})
    )
    tags = TagField(
        required = False,
        widget = TagAutoCompleteInput(app_label="tasks", model="task")
    )
    
    def __init__(self, user, group, *args, **kwargs):
        self.user = user
        self.group = group
        
        super(EditTaskForm, self).__init__(*args, **kwargs)
        
        if group:
            assignee_queryset = group.member_queryset()
        else:
            assignee_queryset = self.fields["assignee"].queryset
        
        self.fields["assignee"].queryset = assignee_queryset.order_by("username")
        self.fields["summary"].widget.attrs["size"] = 65
        self.fields.keyOrder = [
            "summary",
            "detail",
            "tags",
            "status",
            "assignee",
            "state",
            "resolution",
        ]
        
        if not workflow.is_task_manager(self.instance, user):
            del self.fields["detail"]
        
        if self.instance.assignee != user:
            del self.fields["status"]
        
        self.fields["state"].choices = self.instance.allowable_states(user)
        
        if self.instance.state == "3":
            self.fields["resolution"].widget = ReadOnlyWidget(field=self.instance._meta.get_field("resolution"))
    
    class Meta(TaskForm.Meta):
        fields = [
            "summary",
            "detail",
            "status",
            "assignee",
            "state",
            "tags",
            "resolution"
        ]
    
    def clean_resolution(self):
        if self.cleaned_data["state"] == u"2":
            if not self.cleaned_data["resolution"]:
                raise forms.ValidationError(
                    ugettext("You must provide a resolution to mark this task as resolved")
                )
        return self.cleaned_data["resolution"]
