from datetime import datetime
from sys import stderr

from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_app
from django.contrib.auth.models import User

from tasks.models import Task, TaskHistory
from tasks.widgets import ReadOnlyWidget

from tagging_utils.widgets import TagAutoCompleteInput
from tagging.forms import TagField

class TaskForm(forms.ModelForm):
    def __init__(self, group, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        # @@@ for now this following filtering is commented out until we work out how to do generic membership
        self.fields["assignee"].queryset = self.fields["assignee"].queryset.order_by('username')
        self.fields['summary'].widget.attrs["size"] = 65
    
    def save(self, commit=True):
        
        return super(TaskForm, self).save(commit)
    
    tags = TagField(required=False, widget=TagAutoCompleteInput(app_label='tasks', model='task'))
    
    class Meta:
        model = Task
        fields = ('summary', 'detail', 'assignee', 'tags', 'markup')


class EditTaskForm(forms.ModelForm):
    """
    a form for editing task
    """
    
    
    def __init__(self, user, *args, **kwargs):
        super(EditTaskForm, self).__init__(*args, **kwargs)
        self.user = user        
        self.fields["assignee"].queryset = self.fields["assignee"].queryset.order_by('username')
        self.fields['summary'].widget.attrs["size"] = 55
        self.fields.keyOrder = ["summary","tags", "status", "assignee", "state", "resolution"]
        
        if self.instance.assignee != user:
            del self.fields["status"]
                
        # @@@ for now this following filtering is commented out until we work out how to do generic membership
        # self.fields["assignee"].queryset = self.fields["assignee"].queryset.filter(project=project)
        
        self.fields["state"].choices = self.instance.allowable_states(user)
        
        if self.instance.state == '3':
            self.fields['resolution'].widget = ReadOnlyWidget(field=self.instance._meta.get_field('resolution'))
    
    # TODO: work on this for CPC ticket #131
    def save(self, commit=False):            
        
        return super(EditTaskForm, self).save(True)
        
    status = forms.CharField(required=False, widget=forms.TextInput(attrs={'size':'50', 'maxlength': '100'}))
    tags = TagField(required=False, widget=TagAutoCompleteInput(app_label='tasks', model='task'))
    
    class Meta(TaskForm.Meta):
        fields = ('summary','status', 'assignee', 'state', 'tags', 'resolution')

class SearchTaskForm(forms.Form):
    
    search = forms.CharField(label="Search before adding a task",initial="search")
    action = forms.CharField(initial="search",widget=forms.HiddenInput)