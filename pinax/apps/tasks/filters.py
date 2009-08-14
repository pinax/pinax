from django import forms

import django_filters as filters

from tasks.models import Task


class TaskFilter(filters.FilterSet):
    
    state = filters.MultipleChoiceFilter(
        choices = Task.STATE_CHOICES,
        widget = forms.CheckboxSelectMultiple,
    )
    
    class Meta:
        model = Task
        fields = ["state"]