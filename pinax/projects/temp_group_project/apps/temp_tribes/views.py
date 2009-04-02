from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

if "friends" in settings.INSTALLED_APPS:
    from friends.models import Friendship
    friends = True
else:
    friends = False

from threadedcomments.models import ThreadedComment

from wiki.models import Article
from wiki.views import get_ct

from temp_tribes.models import Tribe
from temp_tribes.forms import *

# @@@ from microblogging.models import TweetInstance

# @@@ this needs to be rewritten
TOPIC_COUNT_SQL = """
SELECT COUNT(*)
FROM temp_tribes_topic
WHERE temp_tribes_topic.tribe_id = temp_tribes_tribe.id
"""
MEMBER_COUNT_SQL = """
SELECT COUNT(*)
FROM temp_tribes_tribe_members
WHERE temp_tribes_tribe_members.tribe_id = temp_tribes_tribe.id
"""


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

def tribes(request, template_name="tribes/tribes.html", order=None):
    tribes = Tribe.objects.filter(deleted=False)
    search_terms = request.GET.get('search', '')
    if search_terms:
        tribes = (tribes.filter(name__icontains=search_terms) |
            tribes.filter(description__icontains=search_terms))
    if order == 'least_topics':
        tribes = tribes.extra(select={'topic_count': TOPIC_COUNT_SQL})
        tribes = tribes.order_by('topic_count')
    elif order == 'most_topics':
        tribes = tribes.extra(select={'topic_count': TOPIC_COUNT_SQL})
        tribes = tribes.order_by('-topic_count')
    elif order == 'least_members':
        tribes = tribes.extra(select={'member_count': MEMBER_COUNT_SQL})
        tribes = tribes.order_by('member_count')
    elif order == 'most_members':
        tribes = tribes.extra(select={'member_count': MEMBER_COUNT_SQL})
        tribes = tribes.order_by('-member_count')
    elif order == 'name_ascending':
        tribes = tribes.order_by('name')
    elif order == 'name_descending':
        tribes = tribes.order_by('-name')
    elif order == 'date_oldest':
        tribes = tribes.order_by('-created')
    elif order == 'date_newest':
        tribes = tribes.order_by('created')
    context = {
        'tribes': tribes,
        'search_terms': search_terms,
        'order': order,
    }
    return render_to_response(
        template_name,
        context,
        context_instance=RequestContext(request)
    )

def delete(request, slug, redirect_url=None):
    tribe = get_object_or_404(Tribe, slug=slug)
    if not redirect_url:
        redirect_url = reverse('tribe_list')
    
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
    
    # @@@ photos = tribe.photos.all()
    
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
    # @@@ could make a GR
    articles = Article.objects.filter(
        content_type=get_ct(tribe),
        object_id=tribe.id).order_by('-last_update')
    total_articles = articles.count()
    articles = articles[:5]
    
    # @@@ tweets = TweetInstance.objects.tweets_for(tribe).order_by("-sent")
    
    are_member = request.user in tribe.members.all()
    
    return render_to_response(template_name, {
        "tribe_form": tribe_form,
        "tribe": tribe,
        # @@@ "photos": photos,
        "topics": topics,
        "articles": articles,
        # @@@ "tweets": tweets,
        "total_articles": total_articles,
        "are_member": are_member,
    }, context_instance=RequestContext(request))
