# -*- coding: utf-8 -*-

from datetime import datetime

from django.db import models
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.contrib.auth.models import User

from pinax.utils.importlib import import_module

from tagging.fields import TagField
from tagging.models import Tag

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

workflow = import_module(getattr(settings, "TASKS_WORKFLOW_MODULE", "tasks.workflow"))



class Task(models.Model):
    """
    a task to be performed.
    """
    
    STATE_CHOICES = workflow.STATE_CHOICES
    RESOLUTION_CHOICES = workflow.RESOLUTION_CHOICES
    REVERSE_STATE_CHOICES = workflow.REVERSE_STATE_CHOICES
    
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    group = generic.GenericForeignKey("content_type", "object_id")
    
    # @@@ project = models.ForeignKey(Project, related_name="tasks", verbose_name=_('project'))
    
    summary = models.CharField(_('summary'), max_length=100)
    detail = models.TextField(_('detail'), blank=True)
    markup = models.CharField(_(u'Detail Markup'), max_length=20,
        choices=settings.MARKUP_CHOICES, blank=True)
    creator = models.ForeignKey(User, related_name="created_tasks", verbose_name=_('creator'))
    created = models.DateTimeField(_('created'), default=datetime.now)
    modified = models.DateTimeField(_('modified'), default=datetime.now) # task modified when commented on or when various fields changed
    assignee = models.ForeignKey(User, related_name="assigned_tasks", verbose_name=_('assignee'), null=True, blank=True)
    
    tags = TagField()
    
    # status is a short message the assignee can give on their current status
    status = models.CharField(_('status'), max_length=100, blank=True)
    state = models.CharField(_('state'), max_length=1, choices=workflow.STATE_CHOICES, default=1)
    resolution = models.CharField(_('resolution'), max_length=2, choices=workflow.RESOLUTION_CHOICES, blank=True)
    
    # fields for review and saves
    fields = ('summary', 'detail', 'creator', 'created', 'assignee', 'markup',
        'tags', 'status', 'state', 'resolution')
    
    def __unicode__(self):
        return self.summary
        
    def denudge(self):
        # we remove all nudges for this Task
        
        for nudge in Nudge.objects.filter(task__exact=self):
            nudge.delete()
    
    def save(self, force_insert=False, force_update=False, comment_instance=None, change_owner=None):
        
        # Do the stock save
        self.modified = datetime.now()
        
        super(Task, self).save(force_insert, force_update)
                
    def save_history(self, comment_instance=None, change_owner=None):
        '''Create a new ChangeSet with the old content.'''
        
        # get the task history object
        th = TaskHistory()
        th.task = self
        
        if self.group:
            self.group.associate(th, commit=False)
        
        # save the simple fields
        
        for field in self.fields:
            value = getattr(self, field)
            setattr(th, field, value)


        if change_owner:
            # If a user is provided then we are editing a record.
            # So the owner of the change is the editor.
            th.owner = change_owner
        else:
            # This record is being created right now, hence the assignment
            # of the creator to the task history object's owner field.
            th.owner = self.creator

        # handle the comments
        if comment_instance:
            th.comment = comment_instance.comment
            
        th.save()
    
    
    def allowable_states(self, user):
        """
        return state choices allowed given current state and user
        """
        
        # I'm the relevant state choices.
        choices = []
        
        # I'm the states already allowed for the users
        existing_states = []
        
        for transition in workflow.STATE_TRANSITIONS:
            
            if self.state != str(transition[0]):
                # if the current state does not match a first element in the
                # state transitions we skip to the next transition
                continue
            
            # Fire the validation function.
            if transition[2](self, user):
                
                # grab the new state and state description
                new_state = str(transition[1])
                description = transition[3]

                # build new element
                element = (new_state, description)
                
                # append new element to choices
                choices.append(element)
        
        return choices
    
    def get_absolute_url(self, group=None):
        kwargs = {"id": self.pk}
        if group:
            return group.content_bridge.reverse("task_detail", group, kwargs)
        return reverse("task_detail", kwargs=kwargs)


from threadedcomments.models import ThreadedComment
def new_comment(sender, instance, **kwargs):
    if isinstance(instance.content_object, Task):
        task = instance.content_object
        task.save()
        
        # pass in the instance.user so that the task history owner is recorded
        # as the commenter
        task.save_history(comment_instance=instance,change_owner=instance.user)
        
        group = task.group
        if notification:
            
            if group:
                notify_list = group.member_queryset().exclude(id__exact=instance.user.id) # @@@
            else:
                notify_list = User.objects.all().exclude(id__exact=instance.user.id)
            
            notification.send(notify_list, "tasks_comment", {
                "user": instance.user, "task": task, "comment": instance, "group": group,
            })
models.signals.post_save.connect(new_comment, sender=ThreadedComment)

class TaskHistory(models.Model):
    STATE_CHOICES = workflow.STATE_CHOICES
    RESOLUTION_CHOICES = workflow.RESOLUTION_CHOICES
    REVERSE_STATE_CHOICES = workflow.REVERSE_STATE_CHOICES
    
    task = models.ForeignKey(Task, related_name="history_task", verbose_name=_('tasks'))
    
    # stock task fields.
    # did not subclass because oddly that did not work. WTF?
    # TODO: fix subclass
    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.PositiveIntegerField(null=True)
    group = generic.GenericForeignKey("content_type", "object_id")
    summary = models.CharField(_('summary'), max_length=100)
    detail = models.TextField(_('detail'), blank=True)
    markup = models.CharField(_(u'Detail Markup'), max_length=20,
        choices=settings.MARKUP_CHOICES, blank=True)
    creator = models.ForeignKey(User, related_name="history_created_tasks", verbose_name=_('creator'))
    created = models.DateTimeField(_('created'), default=datetime.now)
    modified = models.DateTimeField(_('modified'), default=datetime.now) # task modified when commented on or when various fields changed
    assignee = models.ForeignKey(User, related_name="history_assigned_tasks", verbose_name=_('assignee'), null=True, blank=True)
    
    tags = TagField()
    
    status = models.CharField(_('status'), max_length=100, blank=True)
    state = models.CharField(_('state'), max_length=1, choices=workflow.STATE_CHOICES, default=1)
    resolution = models.CharField(_('resolution'), max_length=2, choices=workflow.RESOLUTION_CHOICES, default=0, blank=True)
    
    # this stores the comment
    comment = models.TextField(_('comment'), blank=True)
    
    # this stores the owner of this ticket change
    owner = models.ForeignKey(User, related_name="owner", verbose_name=_('Owner'))
    
    def __unicode__(self):
        return 'for ' + str(self.task)
    
    def save(self, force_insert=False, force_update=False):
        self.modified = datetime.now()
        super(TaskHistory, self).save(force_insert, force_update)


class Nudge(models.Model):
    
    nudger = models.ForeignKey(User, related_name="nudger", verbose_name=_('nudger'))
    task = models.ForeignKey(Task, related_name="task_nudge", verbose_name=_('task'))
    modified = models.DateTimeField(_('nudge date'), default=datetime.now)