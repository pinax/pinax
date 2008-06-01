from django.conf.urls.defaults import *

### @@@ is there a better way to wrap all the wiki urls and add to the views the content type / id

from wiki import views as wiki_views
from tribes.models import Tribe
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

TRIBE_CONTENT_TYPE_ID = ContentType.objects.get_for_model(Tribe).id

def wiki_article_list(request, slug):
    tribe = get_object_or_404(Tribe, slug=slug)
    return wiki_views.article_list(request, TRIBE_CONTENT_TYPE_ID, tribe.pk)

def wiki_search_article(request, slug):
    tribe = get_object_or_404(Tribe, slug=slug)
    return wiki_views.search_article(request, TRIBE_CONTENT_TYPE_ID, tribe.pk)

def wiki_view_article(request, slug, title):
    tribe = get_object_or_404(Tribe, slug=slug)
    return wiki_views.view_article(request, TRIBE_CONTENT_TYPE_ID, tribe.pk, title)

def wiki_edit_article(request, slug, title):
    tribe = get_object_or_404(Tribe, slug=slug)
    return wiki_views.edit_article(request, TRIBE_CONTENT_TYPE_ID, tribe.pk, title)

def wiki_article_history(request, slug, title, page):
    tribe = get_object_or_404(Tribe, slug=slug)
    return wiki_views.article_history(request, TRIBE_CONTENT_TYPE_ID, tribe.pk, title, page)

def wiki_view_changeset(request, slug, title, revision):
    tribe = get_object_or_404(Tribe, slug=slug)
    return wiki_views.view_changeset(request, TRIBE_CONTENT_TYPE_ID, tribe.pk, title, revision)

def wiki_revert_revision(request, slug, title):
    tribe = get_object_or_404(Tribe, slug=slug)
    return wiki_views.revert_revision(request, TRIBE_CONTENT_TYPE_ID, tribe.pk, title)

###

urlpatterns = patterns('',
    url(r'^$', 'tribes.views.tribes', name="tribes_list"),
    url(r'^(\w+)/$', 'tribes.views.tribe', name="tribe_detail"),
    
    url(r'^(\w+)/topics/$', 'tribes.views.topics', name="tribe_topics"),
    url(r'^topic/(\d+)/$', 'tribes.views.topic', name="tribe_topic"),
    
    url(r'^(\w+)/wiki/$', wiki_article_list, name="wiki_index"),
    url(r'^(\w+)/wiki/list/$', wiki_article_list, name="wiki_article_list"),
    url(r'^(\w+)/wiki/search/$', wiki_search_article, name="wiki_search_article"),
    url(r'^(\w+)/wiki/(?P<title>\w+)/$', wiki_view_article, name='wiki_article'),
    url(r'^(\w+)/wiki/edit/(?P<title>\w+)/$', wiki_edit_article, name='wiki_edit_article'),
    url(r'^(\w+)/wiki/history/(?P<title>\w+)/(?P<page>\d*)/$', wiki_article_history, name='wiki_article_history'),
    url(r'^(\w+)/wiki/history/(?P<title>\w+)/changeset/(?P<revision>\d+)/$', wiki_view_changeset, name='wiki_changeset'),
    url(r'^(\w+)/wiki/history/(?P<title>\w+)/revert/$', wiki_revert_revision, name='wiki_revert_revision'),
)


