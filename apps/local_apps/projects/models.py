from datetime import datetime

from django.db import models
from django.db.models import signals
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from django.contrib.auth.models import User
from tagging.fields import TagField
from tagging.models import Tag
from photos.models import Pool

try:
    from notification import models as notification
except ImportError:
    notification = None

from wiki.views import get_articles_for_object

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
    
    member_users = models.ManyToManyField(User, through="ProjectMember", verbose_name=_('members'))
    
    deleted = models.BooleanField(_('deleted'), default=False)
    
    # private means only members can see the project
    private = models.BooleanField(_('private'), default=False)
    
    tags = TagField()
    
    photos = generic.GenericRelation(Pool)
    
    # @@@ this might be better as a filter provided by wikiapp
    def wiki_articles(self):
        return get_articles_for_object(self)
    
    def has_member(self, user):
        if user.is_authenticated():
            if ProjectMember.objects.filter(project=self, user=user).count() > 0: # @@@ is there a better way?
                return True
        return False
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return ("project_detail", [self.slug])
    get_absolute_url = models.permalink(get_absolute_url)


class ProjectMember(models.Model):
    project = models.ForeignKey(Project, related_name="members", verbose_name=_('project'))
    user = models.ForeignKey(User, related_name="projects", verbose_name=_('user'))
    
    away = models.BooleanField(_('away'), default=False)
    away_message = models.CharField(_('away_message'), max_length=500)
    away_since = models.DateTimeField(_('away since'), default=datetime.now)


class Topic(models.Model):
    """
    a discussion topic for the project.
    """
    
    project = models.ForeignKey(Project, related_name="topics", verbose_name=_('project'))
    
    title = models.CharField(_('title'), max_length=50)
    creator = models.ForeignKey(User, related_name="created_project_topics", verbose_name=_('creator'))
    created = models.DateTimeField(_('created'), default=datetime.now)
    modified = models.DateTimeField(_('modified'), default=datetime.now) # topic modified when commented on
    body = models.TextField(_('body'), blank=True)
    
    tags = TagField()
    
    def __unicode__(self):
        return self.title
    
    def get_absolute_url(self):
        return ("project_topic", [self.pk])
    get_absolute_url = models.permalink(get_absolute_url)
    
    class Meta:
        ordering = ('-modified', )


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
    
    summary = models.CharField(_('summary'), max_length=100)
    detail = models.TextField(_('detail'), blank=True)
    creator = models.ForeignKey(User, related_name="created_project_tasks", verbose_name=_('creator'))
    created = models.DateTimeField(_('created'), default=datetime.now)
    modified = models.DateTimeField(_('modified'), default=datetime.now) # task modified when commented on or when various fields changed
    assignee = models.ForeignKey(User, related_name="assigned_project_tasks", verbose_name=_('assignee'), null=True, blank=True)
    
    tags = TagField()
    
    # status is a short message the assignee can give on their current status
    status = models.CharField(_('status'), max_length=50, blank=True)
    state = models.CharField(_('state'), max_length=1, choices=STATE_CHOICES, default=1)
    
    def __unicode__(self):
        return self.summary
    
    def save(self, force_insert=False, force_update=False):
        self.modified = datetime.now()
        super(Task, self).save(force_insert, force_update)
    
    def get_absolute_url(self):
        return ("project_task", [self.pk])
    get_absolute_url = models.permalink(get_absolute_url)
    

from threadedcomments.models import ThreadedComment
def new_comment(sender, instance, **kwargs):
    if isinstance(instance.content_object, Topic):
        topic = instance.content_object
        topic.modified = datetime.now()
        topic.save()
        if notification:
            notification.send([topic.creator], "projects_topic_response", {"user": instance.user, "topic": topic, "comment": instance})
    elif isinstance(instance.content_object, Task):
        task = instance.content_object
        task.modified = datetime.now()
        task.save()
        project = task.project
        if notification:
            notification.send(project.member_users.all(), "projects_task_comment", {"user": instance.user, "task": task, "project": project, "comment": instance})
signals.post_save.connect(new_comment, sender=ThreadedComment)
