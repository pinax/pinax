from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext as _

from django.conf import settings

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

from tribes.models import Tribe
from tribes.forms import TribeForm, TribeUpdateForm

TOPIC_COUNT_SQL = """
SELECT COUNT(*)
FROM topics_topic
WHERE
    topics_topic.object_id = tribes_tribe.id AND
    topics_topic.content_type_id = %s
"""
MEMBER_COUNT_SQL = """
SELECT COUNT(*)
FROM tribes_tribe_members
WHERE tribes_tribe_members.tribe_id = tribes_tribe.id
"""

@login_required
def create(request, form_class=TribeForm, template_name="tribes/create.html"):
    tribe_form = form_class(request.POST or None)
    
    if tribe_form.is_valid():
        tribe = tribe_form.save(commit=False)
        tribe.creator = request.user
        tribe.save()
        tribe.members.add(request.user)
        tribe.save()
        if notification:
            # @@@ might be worth having a shortcut for sending to all users
            notification.send(User.objects.all(), "tribes_new_tribe",
                {"tribe": tribe}, queue=True)
        return HttpResponseRedirect(tribe.get_absolute_url())
    
    return render_to_response(template_name, {
        "tribe_form": tribe_form,
    }, context_instance=RequestContext(request))


def tribes(request, template_name="tribes/tribes.html"):
    
    tribes = Tribe.objects.all()
    
    search_terms = request.GET.get('search', '')
    if search_terms:
        tribes = (tribes.filter(name__icontains=search_terms) |
            tribes.filter(description__icontains=search_terms))
    
    content_type = ContentType.objects.get_for_model(Tribe)
    
    tribes = tribes.extra(select=SortedDict([
        ('member_count', MEMBER_COUNT_SQL),
        ('topic_count', TOPIC_COUNT_SQL),
    ]), select_params=(content_type.id,))
    
    return render_to_response(template_name, {
        'tribes': tribes,
        'search_terms': search_terms,
    }, context_instance=RequestContext(request))


def delete(request, group_slug=None, redirect_url=None):
    tribe = get_object_or_404(Tribe, slug=group_slug)
    if not redirect_url:
        redirect_url = reverse('tribe_list')
    
    # @@@ eventually, we'll remove restriction that tribe.creator can't leave tribe but we'll still require tribe.members.all().count() == 1
    if (request.user.is_authenticated() and request.method == "POST" and
            request.user == tribe.creator and tribe.members.all().count() == 1):
        tribe.delete()
        request.user.message_set.create(message=_("Tribe %(tribe_name)s deleted.") % {"tribe_name": tribe.name})
        # no notification required as the deleter must be the only member
    
    return HttpResponseRedirect(redirect_url)


@login_required
def your_tribes(request, template_name="tribes/your_tribes.html"):
    return render_to_response(template_name, {
        "tribes": Tribe.objects.filter(members=request.user).order_by("name"),
    }, context_instance=RequestContext(request))


def tribe(request, group_slug=None, form_class=TribeUpdateForm,
        template_name="tribes/tribe.html"):
    tribe = get_object_or_404(Tribe, slug=group_slug)
    
    tribe_form = form_class(request.POST or None, instance=tribe)
    
    if not request.user.is_authenticated():
        is_member = False
    else:
        is_member = tribe.user_is_member(request.user)
    
    action = request.POST.get('action')
    if action == 'update' and tribe_form.is_valid():
        tribe = tribe_form.save()
    elif action == 'join':
        if not is_member:
            tribe.members.add(request.user)
            request.user.message_set.create(
                message=_("You have joined the tribe %(tribe_name)s") % {"tribe_name": tribe.name})
            is_member = True
            if notification:
                notification.send([tribe.creator], "tribes_created_new_member", {"user": request.user, "tribe": tribe})
                notification.send(tribe.members.all(), "tribes_new_member", {"user": request.user, "tribe": tribe})
        else:
            request.user.message_set.create(
                message=_("You have already joined tribe %(tribe_name)s") % {"tribe_name": tribe.name})
    elif action == 'leave':
        tribe.members.remove(request.user)
        request.user.message_set.create(message="You have left the tribe %(tribe_name)s" % {"tribe_name": tribe.name})
        is_member = False
        if notification:
            pass # @@@ no notification on departure yet
    
    return render_to_response(template_name, {
        "tribe_form": tribe_form,
        "tribe": tribe,
        "group": tribe, # @@@ this should be the only context var for the tribe
        "is_member": is_member,
    }, context_instance=RequestContext(request))
