from django import forms

from topics.models import Topic

class TopicForm(forms.ModelForm):
    
    class Meta:
        model = Topic
        fields = ('title', 'body', 'tags')
