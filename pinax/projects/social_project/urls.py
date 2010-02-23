from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

from account.openid_consumer import PinaxConsumer
from blog.feeds import BlogFeedAll, BlogFeedUser
from bookmarks.feeds import BookmarkFeed
from microblogging.feeds import TweetFeedAll, TweetFeedUser, TweetFeedUserWithFriends



tweets_feed_dict = {"feed_dict": {
    "all": TweetFeedAll,
    "only": TweetFeedUser,
    "with_friends": TweetFeedUserWithFriends,
}}

blogs_feed_dict = {"feed_dict": {
    "all": BlogFeedAll,
    "only": BlogFeedUser,
}}

bookmarks_feed_dict = {"feed_dict": { "": BookmarkFeed }}


handler500 = "pinax.views.server_error"


if settings.ACCOUNT_OPEN_SIGNUP:
    signup_view = "account.views.signup"
else:
    signup_view = "signup_codes.views.signup"


urlpatterns = patterns("",
    url(r"^$", direct_to_template, {
        "template": "homepage.html",
    }, name="home"),
    
    url(r"^admin/invite_user/$", "signup_codes.views.admin_invite_user", name="admin_invite_user"),
    url(r"^account/signup/$", signup_view, name="acct_signup"),
    
    (r"^about/", include("about.urls")),
    (r"^account/", include("account.urls")),
    (r"^openid/(.*)", PinaxConsumer()),
    (r"^bbauth/", include("bbauth.urls")),
    (r"^authsub/", include("authsub.urls")),
    (r"^profiles/", include("profiles.urls")),
    (r"^blog/", include("blog.urls")),
    (r"^invitations/", include("friends_app.urls")),
    (r"^notices/", include("notification.urls")),
    (r"^messages/", include("messages.urls")),
    (r"^announcements/", include("announcements.urls")),
    (r"^tweets/", include("microblogging.urls")),
    (r"^tribes/", include("tribes.urls")),
    (r"^comments/", include("threadedcomments.urls")),
    (r"^robots.txt$", include("robots.urls")),
    (r"^i18n/", include("django.conf.urls.i18n")),
    (r"^bookmarks/", include("bookmarks.urls")),
    (r"^admin/", include(admin.site.urls)),
    (r"^photos/", include("photos.urls")),
    (r"^avatar/", include("avatar.urls")),
    (r"^swaps/", include("swaps.urls")),
    (r"^flag/", include("flag.urls")),
    (r"^locations/", include("locations.urls")),
    
    (r"^feeds/tweets/(.*)/$", "django.contrib.syndication.views.feed", tweets_feed_dict),
    (r"^feeds/posts/(.*)/$", "django.contrib.syndication.views.feed", blogs_feed_dict),
    (r"^feeds/bookmarks/(.*)/?$", "django.contrib.syndication.views.feed", bookmarks_feed_dict),
)

## @@@ for now, we'll use friends_app to glue this stuff together

from photos.models import Image

friends_photos_kwargs = {
    "template_name": "photos/friends_photos.html",
    "friends_objects_function": lambda users: Image.objects.filter(is_public=True, member__in=users),
}

from blog.models import Post

friends_blogs_kwargs = {
    "template_name": "blog/friends_posts.html",
    "friends_objects_function": lambda users: Post.objects.filter(author__in=users),
}

from microblogging.models import Tweet

friends_tweets_kwargs = {
    "template_name": "microblogging/friends_tweets.html",
    "friends_objects_function": lambda users: Tweet.objects.filter(sender_id__in=[user.id for user in users], sender_type__name="user"),
}

from bookmarks.models import Bookmark

friends_bookmarks_kwargs = {
    "template_name": "bookmarks/friends_bookmarks.html",
    "friends_objects_function": lambda users: Bookmark.objects.filter(saved_instances__user__in=users),
    "extra_context": {
        "user_bookmarks": lambda request: Bookmark.objects.filter(saved_instances__user=request.user),
    },
}

urlpatterns += patterns("",
    url("^photos/friends_photos/$", "friends_app.views.friends_objects", kwargs=friends_photos_kwargs, name="friends_photos"),
    url("^blog/friends_blogs/$", "friends_app.views.friends_objects", kwargs=friends_blogs_kwargs, name="friends_blogs"),
    url("^tweets/friends_tweets/$", "friends_app.views.friends_objects", kwargs=friends_tweets_kwargs, name="friends_tweets"),
    url("^bookmarks/friends_bookmarks/$", "friends_app.views.friends_objects", kwargs=friends_bookmarks_kwargs, name="friends_bookmarks"),
)

from tagging.models import TaggedItem

from blog.models import Post
from bookmarks.models import BookmarkInstance
from swaps.models import Offer
from topics.models import Topic
from tribes.models import Tribe
from wiki.models import Article as WikiArticle

tagged_models = (
    dict(title="Blog Posts",
        query=lambda tag : TaggedItem.objects.get_by_model(Post, tag).filter(status=2),
        content_template="pinax_tagging_ext/blogs.html",
    ),
    dict(title="Bookmarks",
        query=lambda tag : TaggedItem.objects.get_by_model(BookmarkInstance, tag),
        content_template="pinax_tagging_ext/bookmarks.html",                
    ),
    dict(title="Photos",
        query=lambda tag: TaggedItem.objects.get_by_model(Image, tag).filter(safetylevel=1),
        content_template="pinax_tagging_ext/photos.html",
    ),    
    dict(title="Swap Offers",
        query=lambda tag : TaggedItem.objects.get_by_model(Offer, tag),            
    ),        
    dict(title="Topics",
        query=lambda tag: TaggedItem.objects.get_by_model(Topic, tag),
    ),
    dict(title="Tribes",
        query=lambda tag: TaggedItem.objects.get_by_model(Tribe, tag),
    ),    
    dict(title="Wiki Articles",
        query=lambda tag: TaggedItem.objects.get_by_model(WikiArticle, tag),
    ),
        

)
tagging_ext_kwargs = {
  'tagged_models':tagged_models,
}

urlpatterns += patterns('',
  url(r'^tags/(?P<tag>.+)/(?P<model>.+)$', 'tagging_ext.views.tag_by_model',
        kwargs=tagging_ext_kwargs, name='tagging_ext_tag_by_model'),
  url(r'^tags/(?P<tag>.+)/$', 'tagging_ext.views.tag',
        kwargs=tagging_ext_kwargs, name='tagging_ext_tag'),
  url(r'^tags/$', 'tagging_ext.views.index', name='tagging_ext_index'),
)

if settings.SERVE_MEDIA:
    urlpatterns += patterns("",
        (r"", include("staticfiles.urls")),
    )
