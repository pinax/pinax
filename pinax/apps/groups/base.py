import datetime
import warnings

from django.db import models
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User


def _get_queryset(klass):
    """
    Returns a QuerySet from a Model, Manager, or QuerySet. Created to make
    get_object_or_404 and get_list_or_404 more DRY.
    
    Pulled from django.shortcuts
    """
    
    if isinstance(klass, QuerySet):
        return klass
    elif isinstance(klass, models.Manager):
        manager = klass
    else:
        manager = klass._default_manager
    return manager.all()


class Group(models.Model):
    """
    a group is a group of users with a common interest
    """
    
    slug = models.SlugField(_('slug'), unique=True)
    name = models.CharField(_('name'), max_length=80, unique=True)
    creator = models.ForeignKey(User, verbose_name=_('creator'), related_name="%(class)s_created")
    created = models.DateTimeField(_('created'), default=datetime.datetime.now)
    description = models.TextField(_('description'))
    # Subclass must provide members field or replace user_is_member()

    def __unicode__(self):
        return self.name
    
    def get_url_kwargs(self):
        return {'group_slug': self.slug}
    
    def user_is_member(self, user):
        return user in self.members.all()
    
    def content_objects(self, model, join=None):
        queryset = _get_queryset(model)
        content_type = ContentType.objects.get_for_model(self)
        if join:
            lookup_kwargs = {
                "%s__object_id" % join: self.id,
                "%s__content_type" % join: content_type,
            }
        else:
            lookup_kwargs = {
                "object_id": self.id,
                "content_type": content_type,
            }
        content_objects = queryset.filter(**lookup_kwargs)
        return content_objects
    
    def associate(self, instance, commit=True):
        instance.object_id = self.id
        instance.content_type = ContentType.objects.get_for_model(self)
        if commit:
            instance.save()
        return instance
    
    class Meta(object):
        abstract = True


class GroupScopedId(models.Model):
    """
    a model to store scoped IDs for tasks (specific to a group)
    """
    
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.IntegerField(null=True, blank=True)
    group = generic.GenericForeignKey()
    
    scoped_number = models.IntegerField()
    
    class Meta:
        abstract = True
        unique_together = (("content_type", "object_id", "scoped_number"),)
