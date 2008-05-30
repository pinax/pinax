from datetime import datetime

from django.db import models
from django.dispatch import dispatcher
from django.db.models import signals
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User

try:
    from notification import models as notification
except ImportError:
    notification = None


class Tribe(models.Model):
    """
    a tribe is a group of users with a common interest
    """
    
    slug = models.SlugField(_('slug'), unique=True)
    name = models.CharField(_('name'), max_length=80, unique=True)
    creator = models.ForeignKey(User, related_name="created_groups", verbose_name=_('creator'))
    created = models.DateTimeField(_('created'), default=datetime.now)
    description = models.TextField(_('description'))
    members = models.ManyToManyField(User, verbose_name=_('members'))
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return ("tribe_detail", [self.slug])
    get_absolute_url = models.permalink(get_absolute_url)
    
    class Admin:
        list_display = ('name', 'creator', 'created',)


class Topic(models.Model):
    """
    a discussion topic for the tribe.
    """
    
    tribe = models.ForeignKey(Tribe, related_name="topics", verbose_name=_('tribe'))
    
    title = models.CharField(_('title'), max_length="50")
    creator = models.ForeignKey(User, related_name="created_topics", verbose_name=_('creator'))
    created = models.DateTimeField(_('created'), default=datetime.now)
    body = models.TextField(_('body'), blank=True)
    
    def __unicode__(self):
        return self.title
    
    def get_absolute_url(self):
        return ("tribe_topic", [self.pk])
    get_absolute_url = models.permalink(get_absolute_url)
    
    class Meta:
        ordering = ('-created', )
    
    class Admin:
        list_display = ('title', )


if notification:
    from threadedcomments.models import ThreadedComment
    def new_comment(sender, instance):
        if isinstance(instance.content_object, Topic):
            topic = instance.content_object
            notification.send([topic.creator], "tribes_topic_response", "%(user)s has responded to your topic '%(topic)s'.", {"user": instance.user, "topic": topic})
    dispatcher.connect(new_comment, signal=signals.post_save, sender=ThreadedComment)
