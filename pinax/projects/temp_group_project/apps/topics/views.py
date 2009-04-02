import os

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, Http404
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import select_template
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

from threadedcomments.models import ThreadedComment

from topics.forms import TopicForm
from topics.models import Topic

class ContentApp(object):
    def __init__(self, group_model, content_app_name):
        self.group_model = group_model
        self.content_app_name = content_app_name
    
    def render(self, template_name, context, context_instance=None):
        ctype = ContentType.objects.get_for_model(self.group_model)
        return render_to_response([
            '%s/%s/%s' % (ctype.app_label, self.content_app_name, template_name),
            '%s/%s' % (self.content_app_name, template_name),
        ], context, context_instance=context_instance)
    
    def get_group(self, slug):
        return self.group_model._default_manager.get(slug=slug)

def topics(request, group_slug=None, form_class=TopicForm, template_name="topics.html", app=None):

    try:
        group = app.get_group(group_slug)
    except ObjectDoesNotExist:
        raise Http404

    is_member = request.user.is_authenticated() and group.user_is_member(request.user) or False

    if request.method == "POST":
        if request.user.is_authenticated():
            if is_member:
                topic_form = form_class(request.POST)
                if topic_form.is_valid():
                    topic = topic_form.save(commit=False)
                    topic.group = group
                    topic.creator = request.user
                    topic.save()
                    request.user.message_set.create(message="You have started the topic %s" % topic.title)
                    topic_form = form_class() # @@@ is this the right way to reset it?
            else:
                request.user.message_set.create(message="You are not a member and so cannot start a new topic")
                topic_form = form_class()
        else:
            return HttpResponseForbidden()
    else:
        topic_form = form_class()


    topics = group.get_related_objects(Topic)

    return app.render(template_name, {
        "group": group,
        "topic_form": topic_form,
        "is_member": is_member,
        "topics": topics,
    }, context_instance=RequestContext(request))


def topic(request, topic_id, edit=False, template_name="topic.html", app=None):
    topic = get_object_or_404(Topic, id=topic_id)

    if request.method == "POST" and edit == True and \
        (request.user == topic.creator or request.user == topic.group.creator):
        topic.body = request.POST["body"]
        topic.save()
        return HttpResponseRedirect(topic.get_absolute_url())

    return app.render(template_name, {
        'topic': topic,
        'edit': edit,
    }, context_instance=RequestContext(request))


def topic_delete(request, pk, app=None):
    topic = Topic.objects.get(pk=pk)

    if request.method == "POST" and (request.user == topic.creator or \
        request.user == topic.group.creator): 
        if forums:
            ThreadedComment.objects.all_for_object(topic).delete()
        topic.delete()

    return HttpResponseRedirect(request.POST["next"])
