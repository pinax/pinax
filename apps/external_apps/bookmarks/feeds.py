from atomformat import Feed
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from bookmarks.models import Bookmark
from django.template.defaultfilters import linebreaks, escape, capfirst
from datetime import datetime

ITEMS_PER_FEED = getattr(settings, 'PINAX_ITEMS_PER_FEED', 20)

class BookmarkFeed(Feed):
    def item_id(self, bookmark):
        return bookmark.url
    
    def item_title(self, bookmark):
        return bookmark.description
    
    def item_updated(self, bookmark):
        return bookmark.added
    
    def item_published(self, bookmark):
        return bookmark.added
    
    def item_content(self, bookmark):
        return {"type" : "html", }, linebreaks(escape(bookmark.note))
    
    def item_links(self, bookmark):
        return [{"href" : self.item_id(bookmark)}]
    
    def item_authors(self, bookmark):
        return [{"name" : bookmark.adder.username}]

    def feed_id(self):
        return 'http://%s/feeds/bookmarks/' % Site.objects.get_current().domain
    
    def feed_title(self):
        return 'Bookmark Feed'

    def feed_updated(self):
        qs = Bookmark.objects.all()
        # We return an arbitrary date if there are no results, because there
        # must be a feed_updated field as per the Atom specifications, however
        # there is no real data to go by, and an arbitrary date can be static.
        if qs.count() == 0:
            return datetime(year=2008, month=7, day=1)
        return qs.latest('added').added

    def feed_links(self):
        absolute_url = reverse('bookmarks.views.bookmarks')
        complete_url = "http://%s%s" % (
                Site.objects.get_current().domain,
                absolute_url,
            )
        return ({'href': complete_url},)

    def items(self):
        return Bookmark.objects.order_by("-added")[:ITEMS_PER_FEED]
