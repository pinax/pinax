from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from blog.models import Post
from tagging.models import Tag, TaggedItem
from photos.models import Photos

def tags(request, tag):
    tag = get_object_or_404(Tag, name=tag)
    alltags = TaggedItem.objects.get_by_model(Post, tag)
    phototags = TaggedItem.objects.get_by_model(Photos, tag)
    return render_to_response('tags/index.html', {
        'tag': tag,
        'alltags': alltags,
        'phototags': phototags,
    }, RequestContext(request))