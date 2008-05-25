from datetime import datetime

from django.db import models
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User

# relational databases are a terrible way to do
# multicast messages (just ask Twitter) but here you have it :-)

import re
ref_re = re.compile("@(\w+)")
reply_re = re.compile("^@(\w+)")

def make_link(text):
    username = text.group(1)
    return """@<a href="/profiles/%s/">%s</a>""" % (username, username)

def format_tweet(text):
    return ref_re.sub(make_link, escape(text))
    
class Tweet(models.Model):
    """
    a single tweet from a user
    """
    
    text = models.CharField(_('text'), max_length=140)
    sender = models.ForeignKey(User, related_name="sent_tweets", verbose_name=_('sender'))
    sent = models.DateTimeField(_('sent'))
    
    def html(self):
        return format_tweet(self.text)
    
    class Meta:
        ordering = ('-sent', )
    
    class Admin:
        list_display = ('id', 'sender', 'text',)

class TweetInstance(models.Model):
    """
    the appearance of a tweet in a follower's timeline
    
    denormalized for better performance
    """
    
    text = models.CharField(_('text'), max_length=140)
    sender = models.ForeignKey(User, related_name="sent_tweet_instances", verbose_name=_('sender'))
    recipient = models.ForeignKey(User, related_name="received_tweet_instances", verbose_name=_('recipient'))
    sent = models.DateTimeField(_('sent'))
    
    def html(self):
        return format_tweet(self.text)
    
    class Admin:
        list_display = ('id', 'sender', 'text', 'recipient',)

def tweet(user, text):
    now = datetime.now()
    Tweet(text=text, sender=user, sent=now).save()
    recipients = set() # keep track of who's received it
    for follower in (following.follower for following in user.followers.all()):
        recipients.add(follower)
    # add sender
    recipients.add(user)
    # if starts with @user send it to them too even if not following
    match = reply_re.match(text)
    if match:
        try:
            recipients.add(User.objects.get(username=match.group(1)))
        except User.DoesNotExist:
            pass # oh well
    for recipient in recipients:
        TweetInstance(text=text, sender=user, recipient=recipient, sent=now).save()


class FollowingManager(models.Manager):
    
    def is_following(self, follower, followed):
        try:
            following = self.get(follower=follower, followed=followed)
            return True
        except Following.DoesNotExist:
            return False
    
    def follow(self, follower, followed):
        if follower != followed and not self.is_following(follower, followed):
            Following(follower=follower, followed=followed).save()
    
    def unfollow(self, follower, followed):
        try:
            following = self.get(follower=follower, followed=followed)
            following.delete()
        except Following.DoesNotExist:
            pass    


class Following(models.Model):
    
    follower = models.ForeignKey(User, related_name="followed", verbose_name=_('follower'))
    followed = models.ForeignKey(User, related_name="followers", verbose_name=_('followed'))
    
    objects = FollowingManager()
    
    class Admin:
        list_display = ('id', 'follower', 'followed',)


