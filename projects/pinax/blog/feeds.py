from atomformat import Feed
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from blog.models import Post
from django.template.defaultfilters import linebreaks, escape, capfirst
from datetime import datetime
from friends.models import friend_set_for

ITEMS_PER_FEED = getattr(settings, 'PINAX_ITEMS_PER_FEED', 20)

class BasePostFeed(Feed):
    def item_id(self, post):
        return "http://%s%s" % (
            Site.objects.get_current().domain,
            post.get_absolute_url(),
        )
    
    def item_title(self, post):
        return post.title
    
    def item_updated(self, post):
        return post.updated_at
    
    def item_published(self, post):
        return post.created_at
    
    def item_content(self, post):
        return {"type" : "html", }, linebreaks(escape(post.body))
    
    def item_links(self, post):
        return [{"href" : self.item_id(post)}]
    
    def item_authors(self, post):
        return [{"name" : post.author.username}]

class BlogFeedAll(BasePostFeed):
    def feed_id(self):
        return 'http://%s/feeds/posts/all/' % Site.objects.get_current().domain
    
    def feed_title(self):
        return 'Blog post feed for all users'

    def feed_updated(self):
        qs = Post.objects.all()
        # We return an arbitrary date if there are no results, because there
        # must be a feed_updated field as per the Atom specifications, however
        # there is no real data to go by, and an arbitrary date can be static.
        if qs.count() == 0:
            return datetime(year=2008, month=7, day=1)
        return qs.latest('created_at').created_at

    def feed_links(self):
        absolute_url = reverse('blog_list_all')
        complete_url = "http://%s%s" % (
                Site.objects.get_current().domain,
                absolute_url,
            )
        return ({'href': complete_url},)

    def items(self):
        return Post.objects.order_by("-created_at")[:ITEMS_PER_FEED]

class BlogFeedUser(BasePostFeed):
    def get_object(self, params):
        return get_object_or_404(User, username=params[0].lower())
    
    def feed_id(self, user):
        return 'http://%s/feeds/posts/only/%s/' % (
            Site.objects.get_current().domain,
            user.username,
        )

    def feed_title(self, user):
        return 'Blog post feed for user %s' % user.username

    def feed_updated(self, user):
        qs = Post.objects.filter(author=user)
        # We return an arbitrary date if there are no results, because there
        # must be a feed_updated field as per the Atom specifications, however
        # there is no real data to go by, and an arbitrary date can be static.
        if qs.count() == 0:
            return datetime(year=2008, month=7, day=1)
        return qs.latest('created_at').created_at

    def feed_links(self, user):
        absolute_url = reverse('blog_list_user', kwargs={'username': user.username})
        complete_url = "http://%s%s" % (
                Site.objects.get_current().domain,
                absolute_url,
            )
        return ({'href': complete_url},)

    def items(self, user):
        return Post.objects.filter(author=user).order_by("-created_at")[:ITEMS_PER_FEED]