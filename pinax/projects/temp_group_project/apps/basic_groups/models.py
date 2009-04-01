from datetime import datetime

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

class BasicGroup(models.Model):
    """
    a group is a group of users with a common interest
    """
    
    slug = models.SlugField(_('slug'), unique=True)
    name = models.CharField(_('name'), max_length=80, unique=True)
    creator = models.ForeignKey(User, related_name="created_groups", verbose_name=_('creator'))
    created = models.DateTimeField(_('created'), default=datetime.now)
    description = models.TextField(_('description'))
    members = models.ManyToManyField(User, verbose_name=_('members')) # @@@ plan to break this out
            
    def __unicode__(self):
        return self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ("group_detail", [self.slug])
    
    def get_url_kwargs(self):
        return {'group_slug': self.slug}
    
    def user_is_member(self, user):
        return user in self.members.all()
    
    def get_related_objects(self, model):
        related_objects = model._default_manager.filter(
            object_id=self.id,
            content_type=ContentType.objects.get_for_model(self)
        )
        return related_objects