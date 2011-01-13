from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

from bookmarks.models import BookmarkInstance
from tagging.models import TaggedItem
from wakawaka.models import WikiPage

from pinax.apps.account.openid_consumer import PinaxConsumer
from pinax.apps.tasks.models import Task
from pinax.apps.topics.models import Topic


handler500 = "pinax.views.server_error"


urlpatterns = patterns("",
    url(r"^$", direct_to_template, {
        "template": "homepage.html",
    }, name="home"),
    url(r"^admin/invite_user/$", "pinax.apps.signup_codes.views.admin_invite_user", name="admin_invite_user"),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^account/", include("pinax.apps.account.urls")),
    url(r"^openid/", include(PinaxConsumer().urls)),
    url(r"^profiles/", include("idios.urls")),
    url(r"^notices/", include("notification.urls")),
    url(r"^announcements/", include("announcements.urls")),
    url(r"^tagging_utils/", include("pinax.apps.tagging_utils.urls")),
    url(r"^attachments/", include("attachments.urls")),
    url(r"^bookmarks/", include("bookmarks.urls")),
    url(r"^tasks/", include("pinax.apps.tasks.urls")),
    url(r"^topics/", include("pinax.apps.topics.urls")),
    url(r"^comments/", include("threadedcomments.urls")),
    url(r"^wiki/", include("wakawaka.urls")),
)


tagged_models = (
    dict(title="Bookmarks",
        query=lambda tag : TaggedItem.objects.get_by_model(BookmarkInstance, tag),
        content_template="pinax_tagging_ext/bookmarks.html",
    ),
    dict(title="Tasks",
        query=lambda tag: TaggedItem.objects.get_by_model(Task, tag),
    ),
    dict(title="Topics",
        query=lambda tag: TaggedItem.objects.get_by_model(Topic, tag),
    ),
    dict(title="Wiki Articles",
        query=lambda tag: TaggedItem.objects.get_by_model(WikiPage, tag),
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
        url(r"", include("staticfiles.urls")),
    )
