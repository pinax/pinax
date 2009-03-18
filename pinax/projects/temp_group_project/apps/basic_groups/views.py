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


MEMBER_COUNT_SQL = """
SELECT COUNT(*)
FROM basic_groups_basicgroup_members
WHERE basic_groups_basicgroup_members.basicgroup_id = basic_groups_basicgroup_members.id
"""

def create(request, form_class=BasicGroupForm, template_name="basic_groups/create.html"):
    
    if request.user.is_authenticated() and request.method == "POST":
        if request.POST["action"] == "create": # @@@ why bother?
            group_form = form_class(request.POST)
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
        else:
            group_form = form_class()
    else:
        group_form = form_class()
    
    return render_to_response(template_name, {
        "group_form": group_form,
    }, context_instance=RequestContext(request))


def groups(request, template_name="basic_groups/groups.html", order=None):
    
    groups = BasicGroup.objects.filter(deleted=False)
    search_terms = request.GET.get('search', '')
    
    if search_terms:
        groups = (groups.filter(name__icontains=search_terms) |
            groups.filter(description__icontains=search_terms))
    
    if order == 'least_members':
        groups = groups.extra(select={'member_count': MEMBER_COUNT_SQL})
        groups = groups.order_by('member_count')
    elif order == 'most_members':
        groups = groups.extra(select={'member_count': MEMBER_COUNT_SQL})
        groups = groups.order_by('-member_count')
    elif order == 'name_ascending':
        groups = groups.order_by('name')
    elif order == 'name_descending':
        groups = groups.order_by('-name')
    elif order == 'date_oldest':
        groups = groups.order_by('-created')
    elif order == 'date_newest':
        groups = groups.order_by('created')
    
    return render_to_response(template_name, {
        'groups': groups,
        'search_terms': search_terms,
        'order': order,
    }, context_instance=RequestContext(request))


def delete(request, slug, redirect_url=None):
    group = get_object_or_404(BasicGroup, slug=slug)
    if not redirect_url:
        redirect_url = reverse('group_list')
    
    # @@@ eventually, we'll remove restriction that group.creator can't leave group but we'll still require group.members.all().count() == 1
    if request.user.is_authenticated() and request.method == "POST" and request.user == group.creator and group.members.all().count() == 1:
        group.deleted = True
        group.save()
        request.user.message_set.create(message="Group %s deleted." % group)
        # no notification required as the deleter must be the only member
    
    return HttpResponseRedirect(redirect_url)


@login_required
def your_groups(request, template_name="basic_groups/your_groups.html"):
    return render_to_response(template_name, {
        "groups": BasicGroup.objects.filter(deleted=False, members=request.user).order_by("name"),
    }, context_instance=RequestContext(request))


def group(request, slug, form_class=BasicGroupUpdateForm, template_name="basic_groups/group.html"):
    group = get_object_or_404(BasicGroup, slug=slug)
    
    if group.deleted:
        raise Http404
    
    if request.user.is_authenticated() and request.method == "POST":
        if request.POST["action"] == "update" and request.user == group.creator:
            group_form = form_class(request.POST, instance=group)
            if group_form.is_valid():
                group = group_form.save()
        else:
            group_form = form_class(instance=group)
        if request.POST["action"] == "join":
            group.members.add(request.user)
            request.user.message_set.create(message="You have joined the group %s" % group.name)
            if notification:
                notification.send([group.creator], "groups_created_new_member", {"user": request.user, "group": group})
                notification.send(group.members.all(), "groups_new_member", {"user": request.user, "group": group})
        elif request.POST["action"] == "leave":
            group.members.remove(request.user)
            request.user.message_set.create(message="You have left the group %s" % group.name)
            if notification:
                pass # @@@ no notification on departure yet
    else:
        group_form = form_class(instance=group)
    
    are_member = request.user in group.members.all()
    
    return render_to_response(template_name, {
        "group_form": group_form,
        "group": group,
        "are_member": are_member,
    }, context_instance=RequestContext(request))
