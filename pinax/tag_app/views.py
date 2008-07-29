from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from blog.models import Post
from tagging.models import Tag, TaggedItem
from photos.models import Photos

from projects.models import Project, Topic, Task

def tags(request, tag):
    tag = get_object_or_404(Tag, name=tag)
    alltags = TaggedItem.objects.get_by_model(Post, tag)
    phototags = TaggedItem.objects.get_by_model(Photos, tag)
    
    project_tags = TaggedItem.objects.get_by_model(Project, tag)
    project_topic_tags = TaggedItem.objects.get_by_model(Topic, tag)
    project_task_tags = TaggedItem.objects.get_by_model(Task, tag)
    
    return render_to_response('tags/index.html', {
        'tag': tag,
        'alltags': alltags,
        'phototags': phototags,
        'project_tags': project_tags,
        'project_topic_tags': project_topic_tags,
        'project_task_tags': project_task_tags,
    }, RequestContext(request))