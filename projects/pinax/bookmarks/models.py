from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User

class Bookmark(models.Model):
    
    url = models.URLField(unique=True)
    description = models.CharField(_('description'), max_length=100)
    note = models.TextField(_('note'), blank=True)
    
    adder = models.ForeignKey(User, related_name="added_bookmarks", verbose_name=_('adder'))
    added = models.DateTimeField(_('added'), default=datetime.now)
    
    class Meta:
        ordering = ('-added', )
    
    class Admin:
        list_display = ('url', 'description', 'added', 'adder',)

