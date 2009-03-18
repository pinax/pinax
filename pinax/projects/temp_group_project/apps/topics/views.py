from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, Http404
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

from threadedcomments.models import ThreadedComment

from topics.forms import TopicForm


def topics(request, get_group, user_is_member, new_topic_callback,
    group_slug, form_class=TopicForm, template_name="topics/topics.html"):
    
    try:
        group = get_group(request, group_slug)
    except ObjectDoesNotExist:
        raise Http404
    
    are_member = user_is_member(request, group)
    
    if request.method == "POST":
        if request.user.is_authenticated():
            if are_member:
                topic_form = form_class(request.POST)
                if topic_form.is_valid():
                    topic = topic_form.save(commit=False)
                    topic.group = group
                    topic.creator = request.user
                    topic.save()
                    request.user.message_set.create(message="You have started the topic %s" % topic.title)
                    new_topic_callback(request, topic)
                    topic_form = form_class() # @@@ is this the right way to reset it?
            else:
                request.user.message_set.create(message="You are not a member and so cannot start a new topic")
                topic_form = form_class()
        else:
            return HttpResponseForbidden()
    else:
        topic_form = form_class()
    
    return render_to_response(template_name, {
        "group": group,
        "topic_form": topic_form,
        "are_member": are_member,
    }, context_instance=RequestContext(request))


def topic(request, id, edit=False, template_name="tribes/topic.html"):
    topic = get_object_or_404(Topic, id=id)
    
    if topic.tribe.deleted:
        raise Http404
    
    if request.method == "POST" and edit == True and \
        (request.user == topic.creator or request.user == topic.tribe.creator):
        topic.body = request.POST["body"]
        topic.save()
        return HttpResponseRedirect(reverse('tribe_topic', args=[topic.id]))
    return render_to_response(template_name, {
        'topic': topic,
        'edit': edit,
    }, context_instance=RequestContext(request))


def topic_delete(request, pk):
    topic = Topic.objects.get(pk=pk)
    
    if topic.tribe.deleted:
        raise Http404
    
    if request.method == "POST" and (request.user == topic.creator or \
        request.user == topic.tribe.creator): 
        if forums:
            ThreadedComment.objects.all_for_object(topic).delete()
        topic.delete()
    
    return HttpResponseRedirect(request.POST["next"])
