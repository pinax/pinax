from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

from bookmarks.models import BookmarkInstance
from tagging.models import TaggedItem
from wiki.models import Article as WikiArticle

from pinax.apps.account.openid_consumer import PinaxConsumer
from pinax.apps.blog.models import Post
from pinax.apps.photos.models import Image
from pinax.apps.projects.models import Project
from pinax.apps.tasks.models import Task
from pinax.apps.topics.models import Topic



handler500 = "pinax.views.server_error"


urlpatterns = patterns("",
    url(r"^$", direct_to_template, {
        "template": "homepage.html",
    }, name="home"),
    
    url(r"^admin/invite_user/$", "pinax.apps.signup_codes.views.admin_invite_user", name="admin_invite_user"),
    url(r"^account/signup/$", "pinax.apps.signup_codes.views.signup", name="acct_signup"),
    
    (r"^account/", include("pinax.apps.account.urls")),
    (r"^openid/(.*)", PinaxConsumer()),
    (r"^profiles/", include("pinax.apps.basic_profiles.urls")),
    (r"^notices/", include("notification.urls")),
    (r"^announcements/", include("announcements.urls")),
    (r"^tagging_utils/", include("pinax.apps.tagging_utils.urls")),
    (r"^attachments/", include("attachments.urls")),
    (r"^bookmarks/", include("bookmarks.urls")),
    (r"^tasks/", include("pinax.apps.tasks.urls")),
    (r"^topics/", include("pinax.apps.topics.urls")),
    (r"^comments/", include("threadedcomments.urls")),
    (r"^wiki/", include("wiki.urls")),
    
    (r"^admin/", include(admin.site.urls)),
)


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
    dict(title="Projects",
        query=lambda tag: TaggedItem.objects.get_by_model(Project, tag),
    ),
    dict(title="Tasks",
        query=lambda tag: TaggedItem.objects.get_by_model(Task, tag),
    ),
    dict(title="Topics",
        query=lambda tag: TaggedItem.objects.get_by_model(Topic, tag),
    ),
    dict(title="Wiki Articles",
        query=lambda tag: TaggedItem.objects.get_by_model(WikiArticle, tag),
    ),
)
tagging_ext_kwargs = {
    "tagged_models": tagged_models,
}

urlpatterns += patterns("",
  url(r"^tags/(?P<tag>.+)/(?P<model>.+)$", "tagging_ext.views.tag_by_model",
        kwargs=tagging_ext_kwargs, name="tagging_ext_tag_by_model"),
  url(r"^tags/(?P<tag>.+)/$", "tagging_ext.views.tag",
        kwargs=tagging_ext_kwargs, name="tagging_ext_tag"),
  url(r"^tags/$", "tagging_ext.views.index", name="tagging_ext_index"),
)


if settings.SERVE_MEDIA:
    urlpatterns += patterns("",
        (r"", include("staticfiles.urls")),
    )
