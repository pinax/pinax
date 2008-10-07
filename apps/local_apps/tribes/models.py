from datetime import datetime

from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic


from django.contrib.auth.models import User

from tagging.fields import TagField
from photos.models import Pool

try:
    from notification import models as notification
except ImportError:
    notification = None

from wiki.views import get_articles_for_object

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
    
    deleted = models.BooleanField(_('deleted'), default=False)
    
    tags = TagField()
    
    photos = generic.GenericRelation(Pool)
    
    # @@@ this might be better as a filter provided by wikiapp
    def wiki_articles(self):
        return get_articles_for_object(self)
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return ("tribe_detail", [self.slug])
    get_absolute_url = models.permalink(get_absolute_url)


class Topic(models.Model):
    """
    a discussion topic for the tribe.
    """
    
    tribe = models.ForeignKey(Tribe, related_name="topics", verbose_name=_('tribe'))
    
    title = models.CharField(_('title'), max_length=50)
    creator = models.ForeignKey(User, related_name="created_topics", verbose_name=_('creator'))
    created = models.DateTimeField(_('created'), default=datetime.now)
    modified = models.DateTimeField(_('modified'), default=datetime.now) # topic modified when commented on
    body = models.TextField(_('body'), blank=True)
    
    tags = TagField()
    
    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return ("tribe_topic", [self.pk])
    get_absolute_url = models.permalink(get_absolute_url)
    
    class Meta:
        ordering = ('-modified', )


from threadedcomments.models import ThreadedComment
def new_comment(sender, instance, **kwargs):
    if isinstance(instance.content_object, Topic):
        topic = instance.content_object
        topic.modified = datetime.now()
        topic.save()
        if notification:
            notification.send([topic.creator], "tribes_topic_response", {"user": instance.user, "topic": topic})
signals.post_save.connect(new_comment, sender=ThreadedComment)
