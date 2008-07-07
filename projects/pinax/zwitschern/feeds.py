from atomformat import Feed
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from zwitschern.models import Tweet, TweetInstance
from django.template.defaultfilters import linebreaks, escape, capfirst
from datetime import datetime

ITEMS_PER_FEED = getattr(settings, 'PINAX_ITEMS_PER_FEED', 20)


class BaseTweetFeed(Feed):
    def item_id(self, tweet):
        return "http://%s%s#%s" % (
            Site.objects.get_current().domain,
            reverse('zwitschern.views.single', args=[tweet.id,]),
            tweet.id,
        )
    
    def item_title(self, tweet):
        return tweet.text
    
    def item_updated(self, tweet):
        return tweet.sent
    
    def item_published(self, tweet):
        return tweet.sent
    
    def item_content(self, tweet):
        return {"type" : "html", }, linebreaks(escape(tweet.html()))
    
    def item_links(self, tweet):
        return [{"href" : self.item_id(tweet)}]
    
    def item_authors(self, tweet):
        return [{"name" : tweet.sender.username}]


class TweetFeedAll(BaseTweetFeed):
    def feed_id(self):
        return 'http://%s/feeds/tweets/all/' % Site.objects.get_current().domain
    
    def feed_title(self):
        return 'Tweets Feed for all users'
    
    def feed_updated(self):
        qs = Tweet.objects.all()
        # We return an arbitrary date if there are no results, because there
        # must be a feed_updated field as per the Atom specifications, however
        # there is no real data to go by, and an arbitrary date can be static.
        if qs.count() == 0:
            return datetime(year=2008, month=7, day=1)
        return qs.latest('sent').sent
    
    def feed_links(self):
        absolute_url = reverse('profiles.views.profiles')
        complete_url = "http://%s%s" % (
                Site.objects.get_current().domain,
                absolute_url,
            )
        return ({'href': complete_url},)
    
    def items(self):
        return Tweet.objects.order_by("-sent")[:ITEMS_PER_FEED]


class TweetFeedUser(BaseTweetFeed):
    def get_object(self, params):
        return get_object_or_404(User, username=params[0].lower())

    def feed_id(self, user):
        return 'http://%s/feeds/tweets/only/%s/' % (
            Site.objects.get_current().domain,
            user.username,
        )
    
    def feed_title(self, user):
        return 'Tweets Feed for User %s' % capfirst(user.username)
    
    def feed_updated(self, user):
        qs = Tweet.objects.filter(sender=user)
        # We return an arbitrary date if there are no results, because there
        # must be a feed_updated field as per the Atom specifications, however
        # there is no real data to go by, and an arbitrary date can be static.
        if qs.count() == 0:
            return datetime(year=2008, month=7, day=1)
        return qs.latest('sent').sent
    
    def feed_links(self, user):
        absolute_url = reverse('profiles.views.profile', args=[user.username,])
        complete_url = "http://%s%s" % (
                Site.objects.get_current().domain,
                absolute_url,
            )
        return ({'href': complete_url},)
    
    def items(self, user):
        return Tweet.objects.filter(sender=user).order_by("-sent")[:ITEMS_PER_FEED]


class TweetFeedUserWithFriends(BaseTweetFeed):
    def get_object(self, params):
        return get_object_or_404(User, username=params[0].lower())

    def feed_id(self, user):
        return 'http://%s/feeds/tweets/with_friends/%s/' % (
            Site.objects.get_current().domain,
            user.username,
        )
    
    def feed_title(self, user):
        return 'Tweets Feed for User %s and friends' % capfirst(user.username)
    
    def feed_updated(self, user):
        qs = TweetInstance.objects.tweets_for(user)
        # We return an arbitrary date if there are no results, because there
        # must be a feed_updated field as per the Atom specifications, however
        # there is no real data to go by, and an arbitrary date can be static.
        if qs.count() == 0:
            return datetime(year=2008, month=7, day=1)
        return qs.latest('sent').sent
    
    def feed_links(self, user):
        absolute_url = reverse('profiles.views.profile', args=[user.username,])
        complete_url = "http://%s%s" % (
                Site.objects.get_current().domain,
                absolute_url,
            )
        return ({'href': complete_url},)
    
    def items(self, user):
        return TweetInstance.objects.tweets_for(user).order_by("-sent")[:ITEMS_PER_FEED]
