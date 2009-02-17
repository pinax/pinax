from datetime import datetime

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User

from tagging.fields import TagField
# @@@ from photos.models import Pool

from topics.models import Topic

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

from wiki.views import get_articles_for_object

class Tribe(models.Model):
    """
    a tribe is a group of users with a common interest
    """
    
    slug = models.SlugField(_('slug'), unique=True)
    name = models.CharField(_('name'), max_length=80, unique=True)
    creator = models.ForeignKey(User, related_name="created_tribes", verbose_name=_('creator'))
    created = models.DateTimeField(_('created'), default=datetime.now)
    description = models.TextField(_('description'))
    members = models.ManyToManyField(User, verbose_name=_('members'))
    
    deleted = models.BooleanField(_('deleted'), default=False)
    
    tags = TagField()
    
    topics = generic.GenericRelation(Topic)
    # @@@ photos = generic.GenericRelation(Pool)
    
    # @@@ this might be better as a filter provided by wikiapp
    def wiki_articles(self):
        return get_articles_for_object(self)
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return ("tribe_detail", [self.slug])
    get_absolute_url = models.permalink(get_absolute_url)
