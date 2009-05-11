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

from basic_groups.models import BasicGroup
from basic_groups.forms import BasicGroupForm, BasicGroupUpdateForm


@login_required
def create(request, form_class=BasicGroupForm, template_name="basic_groups/create.html"):
    
    group_form = form_class(request.POST or None)
    
    if group_form.is_valid():
        group = group_form.save(commit=False)
        group.creator = request.user
        group.save()
        group.members.add(request.user)
        group.save()
        if notification:
            # @@@ might be worth having a shortcut for sending to all users
            notification.send(User.objects.all(), "groups_new_group", {"group": group}, queue=True)
        return HttpResponseRedirect(group.get_absolute_url())
    
    return render_to_response(template_name, {
        "group_form": group_form,
    }, context_instance=RequestContext(request))


def groups(request, template_name="basic_groups/groups.html"):
    
    groups = BasicGroup.objects.filter()
    
    return render_to_response(template_name, {
        'groups': groups,
    }, context_instance=RequestContext(request))


def delete(request, group_slug=None, redirect_url=None):
    group = get_object_or_404(BasicGroup, slug=group_slug)
    if not redirect_url:
        redirect_url = reverse('group_list')
    
    # @@@ eventually, we'll remove restriction that group.creator can't leave group but we'll still require group.members.all().count() == 1
    if request.user.is_authenticated() and request.method == "POST" and request.user == group.creator and group.members.all().count() == 1:
        group.delete()
        request.user.message_set.create(message="Group %s deleted." % group)
        # no notification required as the deleter must be the only member
    
    return HttpResponseRedirect(redirect_url)


@login_required
def your_groups(request, template_name="basic_groups/your_groups.html"):
    return render_to_response(template_name, {
        "groups": BasicGroup.objects.filter(members=request.user).order_by("name"),
    }, context_instance=RequestContext(request))


def group(request, group_slug=None, form_class=BasicGroupUpdateForm, template_name="basic_groups/group.html"):
    group = get_object_or_404(BasicGroup, slug=group_slug)
    
    group_form = form_class(request.POST or None, instance=group)
    
    action = request.POST.get('action')
    
    if action == "update" and group_form.is_valid():
        group = group_form.save()
    elif action == "join":
        group.members.add(request.user)
        request.user.message_set.create(message="You have joined the group %s" % group.name)
        if notification:
            notification.send([group.creator], "groups_created_new_member", {"user": request.user, "group": group})
            notification.send(group.members.all(), "groups_new_member", {"user": request.user, "group": group})
    elif action == "leave":
        group.members.remove(request.user)
        request.user.message_set.create(message="You have left the group %s" % group.name)
        if notification:
            pass # @@@ no notification on departure yet
    
    if not request.user.is_authenticated():
        is_member = False
    else:
        is_member = group.user_is_member(request.user)
    
    return render_to_response(template_name, {
        "group_form": group_form,
        "group": group,
        "is_member": is_member,
    }, context_instance=RequestContext(request))
