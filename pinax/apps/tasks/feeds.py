from atomformat import Feed
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.sites.models import Site
from tasks.models import TaskHistory
from django.template.defaultfilters import linebreaks, escape
from datetime import datetime

ITEMS_PER_FEED = getattr(settings, 'PINAX_ITEMS_PER_FEED', 20)

class BaseTaskFeed(Feed):
    def item_id(self, item):
        return "http://%s%s" % (
            Site.objects.get_current().domain,
            item.task.get_absolute_url(),
        )
    
    def item_title(self, item):
        return item.summary
    
    def item_updated(self, item):
        return item.modified
    
    def item_published(self, item):
        return item.created
    
    def item_content(self, item):
        output = item.detail
        if item.status:
            output = '%s\n\nStatus: %s' % (output, item.status)
        if item.comment:
            output = '%s\n\nComment:\n%s' % (output, item.comment)
        
        return {"type" : "html", }, linebreaks(escape(output))
    
    def item_links(self, item):
        return [{"href" : self.item_id(item)}]
    
    def item_authors(self, item):
        return [{"name" : item.owner.username}]
    
    def feed_id(self):
        return 'http://%s/tasks/feeds/all/' % Site.objects.get_current().domain
    
    def feed_title(self):
        return 'Tasks Changes'
    
    def feed_updated(self):
        qs = self.get_qs()
        # We return an arbitrary date if there are no results, because there
        # must be a feed_updated field as per the Atom specifications, however
        # there is no real data to go by, and an arbitrary date can be static.
        if qs.count() == 0:
            return datetime(year=2008, month=7, day=1)
        return qs.latest('modified').modified
    
    def feed_links(self):
        complete_url = "http://%s%s" % (
            Site.objects.get_current().domain,
            reverse('task_list'),
        )
        return ({'href': complete_url},)
    
    def items(self):
        return self.get_qs()[:ITEMS_PER_FEED]
    
    def get_qs(self):
        return TaskHistory.objects.filter(object_id__isnull=True).order_by('-modified')

class AllTaskFeed(BaseTaskFeed):
    pass