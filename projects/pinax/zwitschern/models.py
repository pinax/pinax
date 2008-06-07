from datetime import datetime

from django.db import models
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from tribes.models import Tribe

# relational databases are a terrible way to do
# multicast messages (just ask Twitter) but here you have it :-)

# @@@ need to make @ and # handling more abstract

import re
user_ref_re = re.compile("@(\w+)")
tribe_ref_re = re.compile("(?<!&)#(\w+)")
reply_re = re.compile("^@(\w+)")

def make_user_link(text):
    username = text.group(1)
    return """@<a href="/profiles/%s/">%s</a>""" % (username, username)

def make_tribe_link(text):
    tribe_slug = text.group(1)
    return """#<a href="/tribes/%s/">%s</a>""" % (tribe_slug, tribe_slug)

def format_tweet(text):
    text = escape(text)
    text = user_ref_re.sub(make_user_link, text)
    text = tribe_ref_re.sub(make_tribe_link, text)
    return text
    
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


class TweetInstanceManager(models.Manager):
    
    def tweets_for(self, recipient):
        recipient_type = ContentType.objects.get_for_model(recipient)
        return TweetInstance.objects.filter(recipient_type=recipient_type, recipient_id=recipient.id)


class TweetInstance(models.Model):
    """
    the appearance of a tweet in a follower's timeline
    
    denormalized for better performance
    """
    
    text = models.CharField(_('text'), max_length=140)
    sender = models.ForeignKey(User, related_name="sent_tweet_instances", verbose_name=_('sender'))
    sent = models.DateTimeField(_('sent'))
    
    # to migrate to generic foreign key, find out the content_type id of User and do something like:
    # ALTER TABLE "zwitschern_tweetinstance"
    #     ADD COLUMN "recipient_type_id" integer NOT NULL
    #     REFERENCES "django_content_type" ("id")
    #     DEFAULT <user content type id>;
    
    # recipient = models.ForeignKey(User, related_name="received_tweet_instances", verbose_name=_('recipient'))
    
    recipient_type = models.ForeignKey(ContentType)
    recipient_id = models.PositiveIntegerField()
    recipient = generic.GenericForeignKey('recipient_type', 'recipient_id')
    
    objects = TweetInstanceManager()
    
    def html(self):
        return format_tweet(self.text)
    
    class Admin:
        list_display = ('id', 'sender', 'text', 'recipient_type', 'recipient_id')

def tweet(user, text):
    now = datetime.now()
    Tweet(text=text, sender=user, sent=now).save()
    recipients = set() # keep track of who's received it
    
    # add the sender's followers
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
    
    # if contains #tribe sent it to that tribe too (the tribe itself, not the members)
    search = tribe_ref_re.search(text)
    if search:
        try:
            recipients.add(Tribe.objects.get(slug=search.group(1)))
        except Tribe.DoesNotExist:
            pass # oh well
    
    # now send to all the recipients
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


