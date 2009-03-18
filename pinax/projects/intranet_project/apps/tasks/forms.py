from datetime import datetime

from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_app
from django.contrib.auth.models import User

from tasks.models import Task


class TaskForm(forms.ModelForm):
    def __init__(self, group, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        # @@@ for now this following filtering is commented out until we work out how to do generic membership
        # self.fields["assignee"].queryset = self.fields["assignee"].queryset.filter(project=project)
    
    class Meta:
        model = Task
        fields = ('summary', 'detail', 'assignee', 'tags')


class EditTaskForm(forms.ModelForm):
    """
    a form for editing task
    """
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(EditTaskForm, self).__init__(*args, **kwargs)
        
        self.fields.keyOrder = ["tags", "status", "assignee", "state"]
        
        if self.instance.assignee != user:
            del self.fields["status"]
        
        # @@@ for now this following filtering is commented out until we work out how to do generic membership
        # self.fields["assignee"].queryset = self.fields["assignee"].queryset.filter(project=project)
        
        self.fields["state"].choices = self.instance.allowable_states(user)
        
        
    status = forms.CharField(required=False, widget=forms.TextInput(attrs={'size':'50', 'maxlength': '100'}))
    
    class Meta(TaskForm.Meta):
        fields = ('status', 'assignee', 'state', 'tags')
