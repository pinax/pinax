import filter as filters

from tasks.models import Task

class TaskFilter(filters.FilterSet):
    
    state = filters.MultipleChoiceFilter(choices=Task.STATE_CHOICES)
    
    class Meta:
        model = Task
        fields = ["state"]