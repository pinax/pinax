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
    private = models.BooleanField(_('private'), default=False)
    
    def __unicode__(self):
        return self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ("project_detail", [self.slug])
    
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


class Task(models.Model):
    """
    a task to be performed for the project.
    """
    
    STATE_CHOICES = (
        ('1', 'open'),
        ('2', 'resolved'), # the assignee thinks it's done
        ('3', 'closed'), # the creator has confirmed it's done
    )
    
    project = models.ForeignKey(Project, related_name="tasks", verbose_name=_('project'))
    
    summary = models.CharField(_('summary'), max_length="100")
    detail = models.TextField(_('detail'), blank=True)
    creator = models.ForeignKey(User, related_name="created_project_tasks", verbose_name=_('creator'))
    created = models.DateTimeField(_('created'), default=datetime.now)
    modified = models.DateTimeField(_('modified'), default=datetime.now) # task modified when commented on or when various fields changed
    assignee = models.ForeignKey(User, related_name="assigned_project_tasks", verbose_name=_('assignee'), null=True, blank=True)
    
    # status is a short message the assignee can give on their current status
    status = models.CharField(_('status'), max_length="50", blank=True)
    state = models.CharField(_('state'), max_length="1", choices=STATE_CHOICES, default=1)
    
    def __unicode__(self):
        return self.summary
    
    def save(self):
        self.modified = datetime.now()
        super(Task, self).save()
    
    @models.permalink
    def get_absolute_url(self):
        return ("project_task", [self.pk])
    
    class Admin:
        pass


from threadedcomments.models import ThreadedComment
def new_comment(sender, instance):
    if isinstance(instance.content_object, Topic):
        topic = instance.content_object
        topic.modified = datetime.now()
        topic.save()
        if notification:
            notification.send([topic.creator], "projects_topic_response", {"user": instance.user, "topic": topic})
    elif isinstance(instance.content_object, Task):
        task = instance.content_object
        task.modified = datetime.now()
        task.save()
        project = task.project
        if notification:
            notification.send(project.members.all(), "projects_task_comment", {"user": instance.user, "task": task, "project": project})
dispatcher.connect(new_comment, signal=signals.post_save, sender=ThreadedComment)
