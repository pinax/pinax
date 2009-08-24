import os

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, Http404
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _ # @@@ really should be ugettext

from django.contrib.auth.models import User

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

from threadedcomments.models import ThreadedComment

from topics.forms import TopicForm
from topics.models import Topic

def topics(request, group_slug=None, form_class=TopicForm, template_name="topics/topics.html", bridge=None):
    
    if bridge:
        try:
            group = bridge.get_group(group_slug)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None
    
    if not request.user.is_authenticated():
        is_member = False
    else:
        if group:
            is_member = group.user_is_member(request.user)
        else:
            is_member = True
    
    if group:
        group_base = bridge.group_base_template()
    else:
        group_base = None
    
    if request.method == "POST":
        if request.user.is_authenticated():
            if is_member:
                topic_form = form_class(request.POST)
                if topic_form.is_valid():
                    topic = topic_form.save(commit=False)
                    if group:
                        group.associate(topic, commit=False)
                    topic.creator = request.user
                    topic.save()
                    request.user.message_set.create(message=_("You have started the topic %(topic_title)s") % {"topic_title": topic.title})
                    topic_form = form_class() # @@@ is this the right way to reset it?
            else:
                request.user.message_set.create(message=_("You are not a member and so cannot start a new topic"))
                topic_form = form_class()
        else:
            return HttpResponseForbidden()
    else:
        topic_form = form_class()
    
    if group:
        topics = group.content_objects(Topic)
    else:
        topics = Topic.objects.filter(object_id=None)
    
    return render_to_response(template_name, {
        "group": group,
        "topic_form": topic_form,
        "is_member": is_member,
        "topics": topics,
        "group_base": group_base,
    }, context_instance=RequestContext(request))


def topic(request, topic_id, group_slug=None, edit=False, template_name="topics/topic.html", bridge=None):
    
    if bridge:
        try:
            group = bridge.get_group(group_slug)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None
    
    if group:
        topics = group.content_objects(Topic)
    else:
        topics = Topic.objects.filter(object_id=None)
    
    topic = get_object_or_404(topics, id=topic_id)
    
    if (request.method == "POST" and edit == True and (request.user == topic.creator or request.user == topic.group.creator)):
        topic.body = request.POST["body"]
        topic.save()
        return HttpResponseRedirect(topic.get_absolute_url(group))
    
    if group:
        group_base = bridge.group_base_template()
    else:
        group_base = None
    
    return render_to_response(template_name, {
        "topic": topic,
        "edit": edit,
        "group": group,
        "group_base": group_base,
    }, context_instance=RequestContext(request))


def topic_delete(request, topic_id, group_slug=None, bridge=None):
    
    if bridge:
        try:
            group = bridge.get_group(group_slug)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None
    
    if group:
        topics = group.content_objects(Topic)
    else:
        topics = Topic.objects.filter(object_id=None)
    
    topic = get_object_or_404(topics, id=topic_id)
    
    if (request.method == "POST" and (request.user == topic.creator or request.user == topic.group.creator)):
        ThreadedComment.objects.all_for_object(topic).delete()
        topic.delete()
    
    return HttpResponseRedirect(request.POST["next"])
