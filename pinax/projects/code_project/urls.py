from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

from tagging.models import TaggedItem
from wakawaka.models import WikiPage

from pinax.apps.account.openid_consumer import PinaxConsumer
from pinax.apps.projects.models import Project
from pinax.apps.tasks.models import Task
from pinax.apps.topics.models import Topic as ProjectTopic



handler500 = "pinax.views.server_error"


urlpatterns = patterns("",
    url(r"^$", direct_to_template, {
        "template": "homepage.html",
    }, name="home"),
    url(r"^admin/invite_user/$", "pinax.apps.signup_codes.views.admin_invite_user", name="admin_invite_user"),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^about/", include("about.urls")),
    url(r"^account/", include("pinax.apps.account.urls")),
    url(r"^openid/", include(PinaxConsumer().urls)),
    url(r"^profiles/", include("idios.urls")),
    url(r"^notices/", include("notification.urls")),
    url(r"^avatar/", include("avatar.urls")),
    url(r"^comments/", include("threadedcomments.urls")),
    url(r"^announcements/", include("announcements.urls")),
    url(r"^tagging_utils/", include("pinax.apps.tagging_utils.urls")),
    url(r"^attachments/", include("attachments.urls")),
    url(r"^projects/", include("pinax.apps.projects.urls")),
)


tagged_models = (
    dict(title="Projects",
        query=lambda tag: TaggedItem.objects.get_by_model(Project, tag),
    ),
    dict(title="Project Topics",
        query=lambda tag: TaggedItem.objects.get_by_model(ProjectTopic, tag),
    ),
    dict(title="Project Tasks",
        query=lambda tag: TaggedItem.objects.get_by_model(Task, tag),
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
