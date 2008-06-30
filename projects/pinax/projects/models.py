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

# @@@ this is based on Tribes -- can we re-use anything?

class Project(models.Model):
    """
    a project is a group of users working together on a common set of tasks.
    """
    
    slug = models.SlugField(_('slug'), unique=True)
    name = models.CharField(_('name'), max_length=80, unique=True)
    creator = models.ForeignKey(User, related_name="created_projects", verbose_name=_('creator'))
    created = models.DateTimeField(_('created'), default=datetime.now)
    description = models.TextField(_('description'))
    members = models.ManyToManyField(User, verbose_name=_('members'))
    
    # private means only members can see the project
    private =models.BooleanField(_('private'), default=False)
    
    def __unicode__(self):
        return self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ("tribe_detail", [self.slug])
    
    class Admin:
        list_display = ('name', 'creator', 'created', 'private')


class Topic(models.Model):
    """
    a discussion topic for the project.
    """
    
    project = models.ForeignKey(Project, related_name="topics", verbose_name=_('project'))
    
    title = models.CharField(_('title'), max_length="50")
    creator = models.ForeignKey(User, related_name="created_project_topics", verbose_name=_('creator'))
    created = models.DateTimeField(_('created'), default=datetime.now)
    modified = models.DateTimeField(_('modified'), default=datetime.now) # topic modified when commented on
    body = models.TextField(_('body'), blank=True)
    
    def __unicode__(self):
        return self.title
    
    @models.permalink
    def get_absolute_url(self):
        return ("project_topic", [self.pk])
    
    class Meta:
        ordering = ('-modified', )
    
    class Admin:
        list_display = ('title', )


from threadedcomments.models import ThreadedComment
def new_comment(sender, instance):
    if isinstance(instance.content_object, Topic):
        topic = instance.content_object
        topic.modified = datetime.now()
        topic.save()
        if notification:
            notification.send([topic.creator], "projects_topic_response", "%(user)s has responded to your topic '%(topic)s'.", {"user": instance.user, "topic": topic})
dispatcher.connect(new_comment, signal=signals.post_save, sender=ThreadedComment)
