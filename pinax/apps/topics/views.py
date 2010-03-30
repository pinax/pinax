import os

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import select_template
from django.utils.translation import ugettext, ugettext_lazy as _

from django.contrib import messages
from django.contrib.auth.models import User

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

from threadedcomments.models import ThreadedComment

from pinax.apps.topics.forms import TopicForm
from pinax.apps.topics.models import Topic



def group_and_bridge(request):
    """
    Given the request we can depend on the GroupMiddleware to provide the
    group and bridge.
    """
    
    # be group aware
    group = getattr(request, "group", None)
    if group:
        bridge = request.bridge
    else:
        bridge = None
    
    return group, bridge


def group_context(group, bridge):
    # @@@ use bridge
    ctx = {
        "group": group,
    }
    if group:
        ctx["group_base"] = bridge.group_base_template()
    return ctx


def topics(request, form_class=TopicForm, template_name="topics/topics.html"):
    
    group, bridge = group_and_bridge(request)
    if group:
        is_member = group.request.user_is_member()
    else:
        is_member = True
    
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
                    messages.add_message(request, messages.SUCCESS,
                        ugettext("You have started the topic %(topic_title)s") % {
                            "topic_title": topic.title
                        }
                    )
                    topic_form = form_class() # @@@ is this the right way to reset it?
            else:
                messages.add_message(request, messages.ERROR,
                    ugettext("You are not a member and so cannot start a new topic")
                )
                topic_form = form_class()
        else:
            return HttpResponseForbidden()
    else:
        topic_form = form_class()
    
    if group:
        topics = group.content_objects(Topic)
    else:
        topics = Topic.objects.filter(object_id=None)
    
    ctx = group_context(group, bridge)
    ctx.update({
        "is_member": is_member,
        "topic_form": topic_form,
        "topics": topics,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))


def topic(request, topic_id, edit=False, template_name="topics/topic.html"):
    
    group, bridge = group_and_bridge(request)
    if group:
        is_member = group.request.user_is_member()
        topics = group.content_objects(Topic)
    else:
        is_member = True
        topics = Topic.objects.filter(object_id=None)
    
    topic = get_object_or_404(topics, id=topic_id)
    
    if (request.method == "POST" and edit == True and (request.user == topic.creator or request.user == topic.group.creator)):
        topic.body = request.POST["body"]
        topic.save()
        return HttpResponseRedirect(topic.get_absolute_url())
    
    ctx = group_context(group, bridge)
    ctx.update({
        "topic": topic,
        "edit": edit,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))


def topic_delete(request, topic_id, group_slug=None, bridge=None):
    
    group, bridge = group_and_bridge(request)
    if group:
        is_member = group.request.user_is_member()
        topics = group.content_objects(Topic)
    else:
        is_member = True
        topics = Topic.objects.filter(object_id=None)
    
    topic = get_object_or_404(topics, id=topic_id)
    
    if (request.method == "POST" and (request.user == topic.creator or request.user == topic.group.creator)):
        ThreadedComment.objects.all_for_object(topic).delete()
        topic.delete()
    
    return HttpResponseRedirect(request.POST["next"])
