from django import forms
from zwitschern.models import Tweet, tweet

try:
    from notification import models as notification
except ImportError:
    notification = None

class TweetForm(forms.ModelForm):
    
    text = forms.CharField(label='',
        widget=forms.Textarea(attrs={
            'rows': '4',
            'cols':'30',
            'id':'new_tweet'
        }))
    
    class Meta:
        model = Tweet
        exclude = ('sender','sent')
        
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(TweetForm, self).__init__(*args, **kwargs)

    def clean_text(self):
        return self.cleaned_data['text'].strip()

    def save(self):
        text = self.cleaned_data["text"]
        tweet_instance = super(TweetForm, self).save(commit=False)
        tweet_instance.sender = self.user
        tweet_instance.save()
        tweet(self.user, text, tweet_instance)
