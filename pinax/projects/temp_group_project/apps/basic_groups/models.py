from datetime import datetime

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User

from tagging.fields import TagField # @@@ see below


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
    
    deleted = models.BooleanField(_('deleted'), default=False) # @@@ should this be supported on basic group and if so, in this manner?
    
    tags = TagField() # @@@ should tags be optional?
    
    def __unicode__(self):
        return self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ("group_detail", [self.slug])
