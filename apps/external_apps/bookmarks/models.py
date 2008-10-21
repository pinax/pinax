from datetime import datetime
import urlparse

from django.db import models
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User

from tagging.fields import TagField
from tagging.models import Tag

"""
A Bookmark is unique to a URL whereas a BookmarkInstance represents a
particular Bookmark saved by a particular person.

This not only enables more than one user to save the same URL as a
bookmark but allows for per-user tagging.
"""

# at the moment Bookmark has some fields that are determined by the
# first person to add the bookmark (the adder) but later we may add
# some notion of voting for the best description and note from
# amongst those in the instances.

class Bookmark(models.Model):
    
    url = models.URLField(unique=True)
    description = models.CharField(_('description'), max_length=100)
    note = models.TextField(_('note'), blank=True)
    
    has_favicon = models.BooleanField(_('has favicon'))
    favicon_checked = models.DateTimeField(_('favicon checked'), default=datetime.now)
    
    adder = models.ForeignKey(User, related_name="added_bookmarks", verbose_name=_('adder'))
    added = models.DateTimeField(_('added'), default=datetime.now)
    
    # tags = TagField()
    
    def get_favicon_url(self, force=False):
        """
        return the URL of the favicon (if it exists) for the site this
        bookmark is on other return None.
        
        If force=True, the URL will be calculated even if it doesn't
        exist.
        """
        if self.has_favicon or force:
            base_url = '%s://%s' % urlparse.urlsplit(self.url)[:2]
            favicon_url = urlparse.urljoin(base_url, 'favicon.ico')
            return favicon_url
        return None
    
    def all_tags(self, min_count=False):
        return Tag.objects.usage_for_model(BookmarkInstance, counts=False, min_count=None, filters={'bookmark': self.id})
    
    def all_tags_with_counts(self, min_count=False):
        return Tag.objects.usage_for_model(BookmarkInstance, counts=True, min_count=None, filters={'bookmark': self.id})
    
    def __unicode__(self):
        return self.url
    
    class Meta:
        ordering = ('-added', )


class BookmarkInstance(models.Model):
    
    bookmark = models.ForeignKey(Bookmark, related_name="saved_instances", verbose_name=_('bookmark'))
    user = models.ForeignKey(User, related_name="saved_bookmarks", verbose_name=_('user'))
    saved = models.DateTimeField(_('saved'), default=datetime.now)
    
    description = models.CharField(_('description'), max_length=100)
    note = models.TextField(_('note'), blank=True)
    
    tags = TagField()
    
    def save(self, force_insert=False, force_update=False):
        try:
            bookmark = Bookmark.objects.get(url=self.url)
        except Bookmark.DoesNotExist:
            # has_favicon=False is temporary as the view for adding bookmarks will change it
            bookmark = Bookmark(url=self.url, description=self.description, note=self.note, has_favicon=False, adder=self.user)
            bookmark.save()
        self.bookmark = bookmark
        super(BookmarkInstance, self).save(force_insert, force_update)
    
    def delete(self):
        bookmark = self.bookmark
        super(BookmarkInstance, self).delete()
        if bookmark.saved_instances.all().count() == 0:
            bookmark.delete()
    
    def __unicode__(self):
        return _("%(bookmark)s for %(user)s") % {'bookmark':self.bookmark, 'user':self.user}
