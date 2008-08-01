from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from blog.models import Post
from tagging.models import Tag, TaggedItem
from photos.models import Photos

from projects.models import Project, Task
from projects.models import Topic as ProjectTopic

from tribes.models import Tribe
from tribes.models import Topic as TribeTopic


def tags(request, tag):
    tag = get_object_or_404(Tag, name=tag)
    alltags = TaggedItem.objects.get_by_model(Post, tag)
    phototags = TaggedItem.objects.get_by_model(Photos, tag)
    
    project_tags = TaggedItem.objects.get_by_model(Project, tag)
    project_topic_tags = TaggedItem.objects.get_by_model(ProjectTopic, tag)
    project_task_tags = TaggedItem.objects.get_by_model(Task, tag)
    
    tribe_tags = TaggedItem.objects.get_by_model(Tribe, tag)
    tribe_topic_tags = TaggedItem.objects.get_by_model(TribeTopic, tag)
    
    return render_to_response('tags/index.html', {
        'tag': tag,
        'alltags': alltags,
        'phototags': phototags,
        'project_tags': project_tags,
        'project_topic_tags': project_topic_tags,
        'project_task_tags': project_task_tags,
        'tribe_tags': tribe_tags,
        'tribe_topic_tags': tribe_topic_tags,
    }, RequestContext(request))