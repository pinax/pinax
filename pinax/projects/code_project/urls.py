from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

from account.openid_consumer import PinaxConsumer



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
    (r"^profiles/", include("basic_profiles.urls")),
    (r"^notices/", include("notification.urls")),
    (r"^avatar/", include("avatar.urls")),
    (r"^comments/", include("threadedcomments.urls")),
    (r"^announcements/", include("announcements.urls")),
    (r"^tagging_utils/", include("tagging_utils.urls")),
    (r"^attachments/", include("attachments.urls")),
    (r"^projects/", include("projects.urls")),
    
    (r"^admin/", include(admin.site.urls)),
)

from tagging.models import TaggedItem

from projects.models import Project
from tasks.models import Task
from topics.models import Topic as ProjectTopic 
from wiki.models import Article as WikiArticle

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
