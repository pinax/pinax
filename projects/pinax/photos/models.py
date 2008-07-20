from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from photologue.models import *
from datetime import datetime

from tagging.fields import TagField
from tagging.models import Tag

from django.utils.translation import ugettext_lazy as _

PUBLISH_CHOICES = (
    (1, _('Public')),
    (2, _('Private')),
)

class PhotoSets(models.Model):
    """docstring for phototribes"""
    name = models.CharField(_('name'), max_length=200)
    description = models.TextField(_('description'))
    publish_type = models.IntegerField(_('publish_type'), choices=PUBLISH_CHOICES, default=1)
    tags = TagField()
    
    class Meta:
        verbose_name = _('photo set')
        verbose_name_plural = _('photo sets')

class Photos(ImageModel):
    """docstring for MemberPhotos"""
    SAFETY_LEVEL = (
        (1, _('Safe')),
        (2, _('Not Safe')),
    )
    title = models.CharField(_('title'), max_length=200)
    title_slug = models.SlugField(_('slug'))
    caption = models.TextField(_('caption'), blank=True)
    date_added = models.DateTimeField(_('date added'), default=datetime.now, editable=False)
    is_public = models.BooleanField(_('is public'), default=True, help_text=_('Public photographs will be displayed in the default views.'))
    member = models.ForeignKey(User, related_name="added_photos", blank=True, null=True)
    safetylevel = models.IntegerField(_('safetylevel'), choices=SAFETY_LEVEL, default=1)
    photoset = models.ManyToManyField(PhotoSets, verbose_name=_('photo set'))
    tags = TagField()
    
    
        