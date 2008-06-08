from atomformat import Feed
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from zwitschern.models import TweetInstance
from django.template.defaultfilters import linebreaks, escape, capfirst

ITEMS_PER_FEED = getattr(settings, 'PINAX_ITEMS_PER_FEED', 20)

class TweetFeed(Feed):
    def get_object(self, params):
        if len(params) > 0:
            try:
                return User.objects.get(username=params[0].lower())
            except User.DoesNotExist:
                pass
        return None

    def feed_id(self, user):
        if user:
            return 'http://%s/feeds/tweets/%s/' % (
                Site.objects.get_current().domain,
                user.username,
            )
        else:
            return 'http://%s/feeds/tweets/' % Site.objects.get_current().domain
    
    def feed_title(self, user):
        if user:
            return 'Tweets Feed for User %s' % capfirst(user.username)
        else:
            return 'Tweets Feed'
    
    def feed_updated(self, user):
        if user:
            qs = TweetInstance.objects.tweets_for(user)
        else:
            qs = TweetInstance.objects.all()
        return qs.latest('sent').sent
    
    def feed_links(self, user):
        if user:
            absolute_url = reverse('profiles.views.profile', args=[user.username,])
        else:
            absolute_url = reverse('profiles.views.profiles')
        complete_url = "http://%s%s" % (
                Site.objects.get_current().domain,
                absolute_url,
            )
        return ({'href': complete_url},)
    
    def items(self, user):
        if user:
            return TweetInstance.objects.tweets_for(user).order_by("-sent")[:ITEMS_PER_FEED]
        else:
            return TweetInstance.objects.order_by("-sent")[:ITEMS_PER_FEED]
    
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