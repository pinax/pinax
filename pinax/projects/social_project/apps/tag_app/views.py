from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from blog.models import Post
from tagging.models import Tag, TaggedItem
from photos.models import Image
from bookmarks.models import BookmarkInstance
# from tribes.models import Tribe
# from tribes.models import Topic as TribeTopic

from wiki.models import Article as WikiArticle


def tags(request, tag, template_name='tags/index.html'):
    tag = get_object_or_404(Tag, name=tag)
    
    alltags = TaggedItem.objects.get_by_model(Post, tag).filter(status=2)
    
    phototags = TaggedItem.objects.get_by_model(Image, tag)
    bookmarktags = TaggedItem.objects.get_by_model(BookmarkInstance, tag)
    
    # tribe_tags = TaggedItem.objects.get_by_model(Tribe, tag).filter(deleted=False)
    # tribe_topic_tags = TaggedItem.objects.get_by_model(TribeTopic, tag).filter(tribe__deleted=False)
    
    # @@@ TODO: tribe_wiki_article_tags and project_wiki_article_tags
    wiki_article_tags = TaggedItem.objects.get_by_model(WikiArticle, tag)
    
    return render_to_response(template_name, {
        'tag': tag,
        'alltags': alltags,
        'phototags': phototags,
        'bookmarktags': bookmarktags,
        # 'tribe_tags': tribe_tags,
        # 'tribe_topic_tags': tribe_topic_tags,
        'wiki_article_tags': wiki_article_tags,
    }, context_instance=RequestContext(request))
