import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

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
    
    def get_related_objects(self, model):
        related_objects = model._default_manager.filter(
            object_id=self.id,
            content_type=ContentType.objects.get_for_model(self)
        )
        return related_objects
    
    class Meta(object):
        abstract = True