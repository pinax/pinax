from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from django.contrib.auth.models import User
from tribes.models import Tribe
from tribes.forms import *

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

def tribes(request):
    if request.user.is_authenticated() and request.method == "POST":
        if request.POST["action"] == "create":
            tribe_form = TribeForm(request.POST)
            if tribe_form.is_valid():
                tribe = tribe_form.save(commit=False)
                tribe.creator = request.user
                tribe.save()
                tribe.members.add(request.user)
                tribe.save()
                tribe_form = TribeForm()
                if notification:
                    # @@@ might be worth having a shortcut for sending to all users
                    notification.send(User.objects.all(), "tribes_new_tribe", "A new tribe %s has been created.", [tribe])
                    if friends: # @@@ might be worth having a shortcut for sending to all friends
                        notification.send((x['friend'] for x in Friendship.objects.friends_for_user(tribe.creator)), "tribes_friend_tribe", "%s has created a new tribe %s.", [tribe.creator, tribe])
                
        else:
            tribe_form = TribeForm()
    else:
        tribe_form = TribeForm()
    
    return render_to_response("tribes/tribes.html", {
        "tribe_form": tribe_form,
        "tribes": Tribe.objects.all().order_by("-created"),
    }, context_instance=RequestContext(request))

def tribe(request, slug):
    tribe = get_object_or_404(Tribe, slug=slug)
    
    if request.user.is_authenticated() and request.method == "POST":
        if request.POST["action"] == "update" and request.user == tribe.creator:
            tribe_form = TribeUpdateForm(request.POST, instance=tribe)
            if tribe_form.is_valid():
                tribe = tribe_form.save()
        if request.POST["action"] == "join":
            tribe.members.add(request.user)
            request.user.message_set.create(message="You have joined the tribe %s" % tribe.name)
            if notification:
                notification.send(tribe.members.all(), "tribes_new_member", "%s has joined the tribe %s.", [request.user, tribe])
                if friends: # @@@ might be worth having a shortcut for sending to all friends
                    notification.send((x['friend'] for x in Friendship.objects.friends_for_user(request.user)), "tribes_friend_joined", "%s has joined the tribe %s.", [request.user, tribe])
        elif request.POST["action"] == "leave":
            tribe.members.remove(request.user)
            request.user.message_set.create(message="You have left the tribe %s" % tribe.name)
            if notification:
                pass # @@@
    
    tribe_form = TribeUpdateForm(instance=tribe)
    topics = tribe.topics.all()[:5]
    are_member = request.user in tribe.members.all()
    
    return render_to_response("tribes/tribe.html", {
        "tribe_form": tribe_form,
        "tribe": tribe,
        "topics": topics,
        "are_member": are_member,
    }, context_instance=RequestContext(request))

def topics(request, slug):
    tribe = get_object_or_404(Tribe, slug=slug)
    
    if request.user.is_authenticated() and request.method == "POST" and request.user in tribe.members.all():
        topic_form = TopicForm(request.POST)
        if topic_form.is_valid():
            topic = topic_form.save(commit=False)
            topic.tribe = tribe
            topic.creator = request.user
            topic.save()
            request.user.message_set.create(message="You have started the topic %s" % topic.title)
            if notification:
                notification.send(tribe.members.all(), "tribes_new_topic", "%(creator)s has started a topic '%(topic)s' in tribe %(tribe)s.", {"creator": request.user, "topic": topic, "tribe": tribe})
            topic_form = TopicForm() # @@@ is this the right way to reset it?
    else:
        topic_form = TopicForm()
    
    return render_to_response("tribes/topics.html", {
        "tribe": tribe,
        "topic_form": topic_form,
    }, context_instance=RequestContext(request))


def topic(request, id):
    topic = get_object_or_404(Topic, id=id)
    
    return render_to_response("tribes/topic.html", {
        'topic': topic,
    }, context_instance=RequestContext(request))