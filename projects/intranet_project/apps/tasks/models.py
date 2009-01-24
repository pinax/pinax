from datetime import datetime

from django.db import models
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.contrib.auth.models import User

from tagging.fields import TagField
from tagging.models import Tag

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None


class Task(models.Model):
    """
    a task to be performed.
    """
    
    STATE_CHOICES = (
        ('1', 'open'),
        ('4', 'in progress'), # the assignee is working on it
        ('5', 'discussion needed'), # discussion needed before work can proceed
        ('6', 'blocked'), # blocked on something or someone (other than discussion)
        ('2', 'resolved'), # the assignee thinks it's done
        ('3', 'closed'), # the creator has confirmed it's done
    )
    REVERSE_STATE_CHOICES = dict((item[1], item[0]) for item in STATE_CHOICES)
    
    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.PositiveIntegerField(null=True)
    group = generic.GenericForeignKey("content_type", "object_id")
    
    # @@@ project = models.ForeignKey(Project, related_name="tasks", verbose_name=_('project'))
    
    summary = models.CharField(_('summary'), max_length=100)
    detail = models.TextField(_('detail'), blank=True)
    creator = models.ForeignKey(User, related_name="created_tasks", verbose_name=_('creator'))
    created = models.DateTimeField(_('created'), default=datetime.now)
    modified = models.DateTimeField(_('modified'), default=datetime.now) # task modified when commented on or when various fields changed
    assignee = models.ForeignKey(User, related_name="assigned_tasks", verbose_name=_('assignee'), null=True, blank=True)
    
    tags = TagField()
    
    # status is a short message the assignee can give on their current status
    status = models.CharField(_('status'), max_length=100, blank=True)
    state = models.CharField(_('state'), max_length=1, choices=STATE_CHOICES, default=1)
    
    def __unicode__(self):
        return self.summary
    
    def save(self, force_insert=False, force_update=False):
        self.modified = datetime.now()
        super(Task, self).save(force_insert, force_update)
    
    def allowable_states(self, user):
        """
        return state choices allowed given current state and user
        """
        
        if self.state == '1': # open
            if user == self.assignee:
                choices = [('1', 'leave open'), ('4', 'in progress'), ('5', 'discussion needed'), ('6', 'blocked'), ('2', 'resolve')]
            elif self.assignee is None:
                choices = [('1', 'leave open'), ('5', 'discussion needed'), ('6', 'blocked')]
            else:
                choices = [('1', 'leave open')]
        elif self.state == '2': # resolved
            if user == self.creator:
                choices = [('2', 'leave resolved'), ('1', 'reopen'), ('3', 'close')]
            else:
                choices = [('2', 'leave resolved'), ('1', 'reopen')]
        elif self.state == '3': # closed
            choices = [('3', 'leave closed'), ('1', 'reopen')]
        elif self.state == '4': # in progress
            if user == self.assignee:
                choices = [('4', 'still in progress'), ('1', 'revert to open'), ('5', 'discussion needed'), ('6', 'blocked'), ('2', 'resolve'), ]
            else:
                choices = [('4', 'still in progress')]
        elif self.state == '5': # discussion needed
            if user == self.assignee:
                choices = [('5', 'discussion still needed'), ('1', 'revert to open'), ('4', 'in progress'), ('6', 'blocked'), ('2', 'resolve')]
            elif self.assignee is None:
                choices = [('5', 'discussion still needed'), ('1', 'revert to open'), ('4', 'in progress'), ('6', 'blocked'), ('2', 'resolve')]
            else:
                choices = [('5', 'discussion still needed')]
        elif self.state == '6': # blocked
            if user == self.assignee:
                choices = [('6', 'still blocked'), ('1', 'revert to open'), ('5', 'discussion needed'), ('4', 'in progress'), ('2', 'resolve')]
            elif self.assignee is None:
                choices = [('6', 'still blocked'), ('1', 'revert to open'), ('5', 'discussion needed'), ('4', 'in progress'), ('2', 'resolve')]
            else:
                choices = [('6', 'still blocked')]
                
        return choices
    
    @models.permalink
    def get_absolute_url(self):
        return ("task_detail", [self.pk])




from threadedcomments.models import ThreadedComment
def new_comment(sender, instance, **kwargs):
    if isinstance(instance.content_object, Task):
        task = instance.content_object
        task.modified = datetime.now()
        task.save()
        group = task.group
        if notification:
            
            if group:
                notify_list = group.member_users.all() # @@@
            else:
                notify_list = User.objects.all()
            
            notification.send(notify_list, "tasks_comment", {
                "user": instance.user, "task": task, "comment": instance, "group": group,
            })
models.signals.post_save.connect(new_comment, sender=ThreadedComment)
