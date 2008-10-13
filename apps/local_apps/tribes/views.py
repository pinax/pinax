from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, Http404

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from tribes.models import Tribe
from tribes.forms import *
from django.core.urlresolvers import reverse

try:
    from notification import models as notification
except ImportError:
    notification = None

try:
    from friends.models import Friendship
    friends = True
except ImportError:
    friends = False

try:
    from threadedcomments.models import ThreadedComment
    forums = True
except ImportError:
    forums = False

try:
    from wiki.models import Article
    from wiki.views import get_ct
    wiki = True
except ImportError:
    wiki = False

from zwitschern.models import TweetInstance


def create(request, form_class=TribeForm, template_name="tribes/create.html"):
    if request.user.is_authenticated() and request.method == "POST":
        if request.POST["action"] == "create":
            tribe_form = form_class(request.POST)
            if tribe_form.is_valid():
                tribe = tribe_form.save(commit=False)
                tribe.creator = request.user
                tribe.save()
                tribe.members.add(request.user)
                tribe.save()
                if notification:
                    # @@@ might be worth having a shortcut for sending to all users
                    notification.send(User.objects.all(), "tribes_new_tribe", {"tribe": tribe}, queue=True)
                    if friends: # @@@ might be worth having a shortcut for sending to all friends
                        notification.send((x['friend'] for x in Friendship.objects.friends_for_user(tribe.creator)), "tribes_friend_tribe", {"tribe": tribe})
                #return render_to_response("base.html", {
                #}, context_instance=RequestContext(request))
                return HttpResponseRedirect(tribe.get_absolute_url())
        else:
            tribe_form = form_class()
    else:
        tribe_form = form_class()
    
    return render_to_response(template_name, {
        "tribe_form": tribe_form,
    }, context_instance=RequestContext(request))


def delete(request, slug, redirect_url=None):
    tribe = get_object_or_404(Tribe, slug=slug)
    if not redirect_url:
        redirect_url = "/tribes/" # @@@ can't use reverse("tribes") -- what is URL name using things?
    
    # @@@ eventually, we'll remove restriction that tribe.creator can't leave tribe but we'll still require tribe.members.all().count() == 1
    if request.user.is_authenticated() and request.method == "POST" and request.user == tribe.creator and tribe.members.all().count() == 1:
        tribe.deleted = True
        tribe.save()
        request.user.message_set.create(message="Tribe %s deleted." % tribe)
        # @@@ no notification as the deleter must be the only member
    
    return HttpResponseRedirect(redirect_url)


def your_tribes(request, template_name="tribes/your_tribes.html"):
    return render_to_response(template_name, {
        "tribes": Tribe.objects.filter(deleted=False, members=request.user).order_by("name"),
    }, context_instance=RequestContext(request))
your_tribes = login_required(your_tribes)

def tribe(request, slug, form_class=TribeUpdateForm,
        template_name="tribes/tribe.html"):
    tribe = get_object_or_404(Tribe, slug=slug)
    
    if tribe.deleted:
        raise Http404
    
    photos = tribe.photos.all()
    
    if request.user.is_authenticated() and request.method == "POST":
        if request.POST["action"] == "update" and request.user == tribe.creator:
            tribe_form = form_class(request.POST, instance=tribe)
            if tribe_form.is_valid():
                tribe = tribe_form.save()
        else:
            tribe_form = form_class(instance=tribe)
        if request.POST["action"] == "join":
            tribe.members.add(request.user)
            request.user.message_set.create(message="You have joined the tribe %s" % tribe.name)
            if notification:
                notification.send([tribe.creator], "tribes_created_new_member", {"user": request.user, "tribe": tribe})
                notification.send(tribe.members.all(), "tribes_new_member", {"user": request.user, "tribe": tribe})
                if friends: # @@@ might be worth having a shortcut for sending to all friends
                    notification.send((x['friend'] for x in Friendship.objects.friends_for_user(request.user)), "tribes_friend_joined", {"user": request.user, "tribe": tribe})
        elif request.POST["action"] == "leave":
            tribe.members.remove(request.user)
            request.user.message_set.create(message="You have left the tribe %s" % tribe.name)
            if notification:
                pass # @@@
    else:
        tribe_form = form_class(instance=tribe)
    
    topics = tribe.topics.all()[:5]
    articles = Article.objects.filter(
        content_type=get_ct(tribe),
        object_id=tribe.id).order_by('-last_update')
    total_articles = articles.count()
    articles = articles[:5]
    
    tweets = TweetInstance.objects.tweets_for(tribe).order_by("-sent")
    
    are_member = request.user in tribe.members.all()
    
    return render_to_response(template_name, {
        "tribe_form": tribe_form,
        "tribe": tribe,
        "photos": photos,
        "topics": topics,
        "articles": articles,
        "tweets": tweets,
        "total_articles": total_articles,
        "are_member": are_member,
    }, context_instance=RequestContext(request))

def topics(request, slug, form_class=TopicForm,
        template_name="tribes/topics.html"):
    tribe = get_object_or_404(Tribe, slug=slug)
    
    if tribe.deleted:
        raise Http404
    
    are_member = False
    if request.user.is_authenticated():
        are_member = request.user in tribe.members.all()
    
    if request.method == "POST":
        if request.user.is_authenticated():
            if are_member:
                topic_form = form_class(request.POST)
                if topic_form.is_valid():
                    topic = topic_form.save(commit=False)
                    topic.tribe = tribe
                    topic.creator = request.user
                    topic.save()
                    request.user.message_set.create(message="You have started the topic %s" % topic.title)
                    if notification:
                        notification.send(tribe.members.all(), "tribes_new_topic", {"topic": topic})
                    topic_form = form_class() # @@@ is this the right way to reset it?
            else:
                request.user.message_set.create(message="You are not a member and so cannot start a new topic")
                topic_form = form_class()
        else:
            return HttpResponseForbidden()
    else:
        topic_form = form_class()
    
    return render_to_response(template_name, {
        "tribe": tribe,
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
