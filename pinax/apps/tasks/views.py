from datetime import date
from datetime import datetime, timedelta
from itertools import chain
from operator import attrgetter


from django.shortcuts import render_to_response, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_app
from django.db.models import Q

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType

from pinax.utils.importlib import import_module

from tagging.models import Tag
from django.utils.translation import ugettext

# Only import dpaste Snippet Model if it's activated
if 'dpaste' in getattr(settings, 'INSTALLED_APPS', []):
    from dpaste.models import Snippet
else:
    Snippet = False

from tasks.models import Task, TaskHistory, Nudge
from tasks.filters import TaskFilter
from tasks.forms import TaskForm, EditTaskForm, SearchTaskForm

workflow = import_module(getattr(settings, "TASKS_WORKFLOW_MODULE", "tasks.workflow"))

try:
    notification = get_app('notification')
except ImproperlyConfigured:
    notification = None


def tasks(request, group_slug=None, template_name="tasks/task_list.html", bridge=None):
    
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
    
    group_by = request.GET.get("group_by")
    
    if group:
        tasks = group.content_objects(Task)
        group_base = bridge.group_base_template()
    else:
        tasks = Task.objects.filter(object_id=None)
        group_base = None
    
    tasks = tasks.select_related("assignee")
    
    # default filtering
    state_keys = dict(workflow.STATE_CHOICES).keys()
    default_states = set(state_keys).difference(
        # don't show these states
        set(["2", "3"])
    )
    
    filter_data = {"state": list(default_states)}
    filter_data.update(request.GET)
    
    task_filter = TaskFilter(filter_data, queryset=tasks)
    
    group_by_querydict = request.GET.copy()
    group_by_querydict.pop("group_by", None)
    group_by_querystring = group_by_querydict.urlencode()
    
    return render_to_response(template_name, {
        "group": group,
        "group_by": group_by,
        "gbqs": group_by_querystring,
        "is_member": is_member,
        "group_base": group_base,
        "task_filter": task_filter,
        "tasks": task_filter.qs,
        "querystring": request.GET.urlencode(),
    }, context_instance=RequestContext(request))


def add_task(request, group_slug=None, secret_id=None, form_class=TaskForm, template_name="tasks/add.html", bridge=None):
    
    if bridge:
        try:
            group = bridge.get_group(group_slug)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None
    
    if group:
        group_base = bridge.group_base_template()
    else:
        group_base = None
    
    if not request.user.is_authenticated():
        is_member = False
    else:
        if group:
            is_member = group.user_is_member(request.user)
        else:
            is_member = True
    
    # If we got an ID for a snippet in url, collect some initial values
    # But only if we could import the Snippet Model so
    if secret_id and Snippet:
        paste = get_object_or_404(Snippet, secret_id=secret_id)
        paste.expires = datetime.now() + timedelta(seconds=3600*24*30*12*100) # Update the expiration time to maximum
        paste.save()
        paste_link = ugettext('Link to the snippet: http://%(domain)s%(link)s\n\n' % {
                                'domain': Site.objects.get_current().domain,
                                'link': reverse('snippet_details', kwargs={'snippet_id': paste.secret_id})
                             })
        initial = {
            'summary': paste.title,
            'detail': paste_link,
        }
    else:
        initial = {}
    
    if request.method == "POST":
        if request.user.is_authenticated():
            task_form = form_class(request.user, group, request.POST)
            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.creator = request.user
                task.group = group
                task.save()
                task.save_history()
                request.user.message_set.create(message="added task '%s'" % task.summary)
                if notification:
                    if group:
                        notify_list = group.member_queryset()
                    else:
                        notify_list = User.objects.all() # @@@
                    notify_list = notify_list.exclude(id__exact=request.user.id)
                    notification.send(notify_list, "tasks_new", {"creator": request.user, "task": task, "group": group})
                if request.POST.has_key('add-another-task'):
                    if group:
                        redirect_to = bridge.reverse("task_add", group)
                    else:
                        redirect_to = reverse("task_add")
                    return HttpResponseRedirect(redirect_to)
                if group:
                    redirect_to = bridge.reverse("task_list", group)
                else:
                    redirect_to = reverse("task_list")
                return HttpResponseRedirect(redirect_to)
    else:
        task_form = form_class(request.user, group, initial=initial)
    
    return render_to_response(template_name, {
        "group": group,
        "is_member": is_member,
        "task_form": task_form,
        "group_base": group_base,
    }, context_instance=RequestContext(request))

@login_required
def nudge(request, id, group_slug=None, bridge=None):
    """ Called when a user nudges a ticket """
    
    if bridge:
        try:
            group = bridge.get_group(group_slug)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None
    
    if group:
        tasks = group.content_objects(Task)
    else:
        tasks = Task.objects.filter(object_id=None)
    
    task = get_object_or_404(tasks, id=id)
    task_url = task.get_absolute_url(group)
    
    nudged = Nudge.objects.filter(task__exact=task, nudger__exact=request.user)
    if nudged:
        # you've already nudged this task.
        nudge = nudged[0]
        nudge.delete()
        message = "You've removed your nudge from this task"
        request.user.message_set.create(message=message)
        return HttpResponseRedirect(task_url)
    
    
    nudge = Nudge(nudger=request.user, task=task)
    nudge.save()
    
    count = Nudge.objects.filter(task__exact=task).count()
    
    # send the message to the user
    message = "%s has been nudged about this task" % task.assignee
    request.user.message_set.create(message=message)
    
    # send out the nudge notification
    if notification:
        notify_list = [task.assignee]
        notification.send(notify_list, "tasks_nudge", {"nudger": request.user, "task": task, "count": count})
    
    return HttpResponseRedirect(task_url)

def task(request, id, group_slug=None, template_name="tasks/task.html", bridge=None):
    
    if bridge:
        try:
            group = bridge.get_group(group_slug)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None
    
    if group:
        tasks = group.content_objects(Task)
        group_base = bridge.group_base_template()
    else:
        tasks = Task.objects.filter(object_id=None)
        group_base = None
    
    task = get_object_or_404(tasks, id=id)
    
    if group:
        notify_list = group.member_queryset()
    else:
        notify_list = User.objects.all()
    notify_list = notify_list.exclude(id__exact=request.user.id)
    
    if not request.user.is_authenticated():
        is_member = False
    else:
        if group:
            is_member = group.user_is_member(request.user)
        else:
            is_member = True
    
    if is_member and request.method == "POST":
        form = EditTaskForm(request.user, group, request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            task.save_history(change_owner=request.user)
            if task.assignee == request.user:
                task.denudge()
            if "status" in form.changed_data:
                request.user.message_set.create(message="updated your status on the task")
                if notification:
                    notification.send(notify_list, "tasks_status", {"user": request.user, "task": task, "group": group})
            if "state" in form.changed_data:
                request.user.message_set.create(message="task marked %s" % task.get_state_display())
                if notification:
                    notification.send(notify_list, "tasks_change", {"user": request.user, "task": task, "group": group, "new_state": task.get_state_display()})
            if "assignee" in form.changed_data:
                request.user.message_set.create(message="assigned task to '%s'" % task.assignee)
                if notification:
                    notification.send(notify_list, "tasks_assignment", {"user": request.user, "task": task, "assignee": task.assignee, "group": group})
            if "tags" in form.changed_data:
                request.user.message_set.create(message="updated tags on the task")
                if notification:
                    notification.send(notify_list, "tasks_tags", {"user": request.user, "task": task, "group": group})
            form = EditTaskForm(request.user, group, instance=task)
    else:
        form = EditTaskForm(request.user, group, instance=task)
    
    # The NUDGE dictionary
    nudge = {}
    nudge['nudgeable'] = False
    
    # get the count of nudges so assignee can see general level of interest.
    nudge['count'] = Nudge.objects.filter(task__exact=task).count()
    
    # get the nudge if you are not the assignee otherwise just a None
    if is_member and request.user != task.assignee and task.assignee:
        nudge['nudgeable'] = True
        try:
            nudge['nudge'] = Nudge.objects.filter(nudger__exact=request.user, task__exact=task)[0]
        except IndexError:
            nudge['nudge'] = None
    
    # get the nudge history
    nudge['history'] = Nudge.objects.filter(task__exact=task)
    
    return render_to_response(template_name, {
        "group": group,
        "nudge": nudge,
        "task": task,
        "is_member": is_member,
        "form": form,
        "group_base": group_base,
    }, context_instance=RequestContext(request))


@login_required
def user_tasks(request, username, group_slug=None, template_name="tasks/user_tasks.html", bridge=None):
    
    if bridge:
        try:
            group = bridge.get_group(group_slug)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None
    
    if group:
        other_user = get_object_or_404(group.member_queryset(), username=username)
        group_base = bridge.group_base_template()
    else:
        other_user = get_object_or_404(User, username=username)
        group_base = None
    
    assigned_tasks = other_user.assigned_tasks.all()
    created_tasks = other_user.created_tasks.all()
    
    if group:
        assigned_tasks = group.content_objects(assigned_tasks)
        created_tasks = group.content_objects(created_tasks)
    else:
        assigned_tasks = assigned_tasks.filter(object_id=None)
        created_tasks = created_tasks.filter(object_id=None)
    
    # default filtering
    state_keys = dict(workflow.STATE_CHOICES).keys()
    default_states = set(state_keys).difference(
        # don't show these states
        set(["2", "3"])
    )
    
    # have to store for each prefix because initial data isn't support on the
    # FilterSet
    filter_data = {
        "a-state": list(default_states),
        "c-state": list(default_states),
        "n-state": list(default_states),
    }
    filter_data.update(request.GET)
    
    assigned_filter = TaskFilter(filter_data, queryset=assigned_tasks, prefix="a")
    created_filter = TaskFilter(filter_data, queryset=created_tasks, prefix="c")
    
    assigned_tasks = assigned_filter.qs
    created_tasks = created_filter.qs
    
    assigned_tasks = assigned_tasks.order_by("state", "-modified") # @@@ filter(project__deleted=False)
    created_tasks = created_tasks.order_by("state", "-modified") # @@@ filter(project__deleted=False)
    
    nudged_tasks = assigned_tasks.extra(
        tables = ["tasks_nudge"],
        where = ["tasks_nudge.id = tasks_task.id"],
    )
    
    nudged_filter = TaskFilter(filter_data, queryset=nudged_tasks, prefix="n")
    nudged_tasks = nudged_filter.qs
    
    site_url = "http://" + Site.objects.get_current().domain
    
    if group:
        url = site_url + bridge.reverse("tasks_mini_list", group)
    else:
        url = site_url + reverse("tasks_mini_list")
    
    bookmarklet = """javascript:(function() {
url = '%s';
window.open(url, 'tasklist', 'height=500, width=250, title=no, location=no,
scrollbars=yes, menubars=no, navigation=no, statusbar=no, directories=no,
resizable=yes, status=no, toolbar=no, menuBar=no');})()""" % url
    
    return render_to_response(template_name, {
        "group": group,
        "assigned_filter": assigned_filter,
        "created_filter": created_filter,
        "nudged_filter": nudged_filter,
        "assigned_tasks": assigned_tasks,
        "created_tasks": created_tasks,
        "nudged_tasks": nudged_tasks,
        "other_user": other_user,
        "bookmarklet": bookmarklet,
        "group_base": group_base,
    }, context_instance=RequestContext(request))


@login_required
def mini_list(request, group_slug=None, template_name="tasks/mini_list.html", bridge=None):
    if bridge:
        try:
            group = bridge.get_group(group_slug)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None
    
    assigned_tasks = request.user.assigned_tasks.all().exclude(state="2").exclude(state="3").order_by("state", "-modified")
    
    if group:
        assigned_tasks = group.content_objects(assigned_tasks)
    else:
        assigned_tasks = assigned_tasks.filter(object_id=None)
    
    return render_to_response(template_name, {
        "group": group,
        "assigned_tasks": assigned_tasks,
    }, context_instance=RequestContext(request))


def focus(request, field, value, group_slug=None, template_name="tasks/focus.html", bridge=None):
    
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
    
    group_by = request.GET.get("group_by")
    
    if group:
        tasks = group.content_objects(Task)
        group_base = bridge.group_base_template()
    else:
        tasks = Task.objects.filter(object_id=None)
        group_base = None
    
    # default filtering
    state_keys = dict(workflow.STATE_CHOICES).keys()
    default_states = set(state_keys).difference(
        # don't show these states
        set(["2", "3"])
    )
    
    # have to store for each prefix because initial data isn't support on the
    # FilterSet
    filter_data = {
        "state": list(default_states),
    }
    filter_data.update(request.GET)
    
    task_filter = TaskFilter(filter_data, queryset=tasks)
    
    if field == "modified":
        try:
            # @@@ this seems hackish and brittle but I couldn't work out another way
            year, month, day = value.split("-")
            # have to int month and day in case zero-padded
            tasks = tasks.filter(modified__year=int(year), modified__month=int(month), modified__day=int(day))
        except:
            tasks = Task.objects.none() # @@@ or throw 404?
    elif field == "state":
        task_filter = None # prevent task filtering
        try:
            state = workflow.REVERSE_STATE_CHOICES[value]
        except KeyError:
            raise Http404
        tasks = tasks.filter(state=state)
    elif field == "assignee":
        if value == "unassigned": # @@@ this means can't have a username 'unassigned':
            tasks = tasks.filter(assignee__isnull=True)
        else:
            try:
                assignee = User.objects.get(username=value)
                tasks = tasks.filter(assignee=assignee)
            except User.DoesNotExist:
                tasks = Task.objects.none() # @@@ or throw 404?
    elif field == "tag":
        try:
            # @@@ is there a better way?
            task_type = ContentType.objects.get_for_model(Task)
            tasks = tasks.filter(id__in=Tag.objects.get(name=value).items.filter(content_type=task_type).values_list("object_id", flat=True))
            # @@@ still need to filter on group if group not None
        except Tag.DoesNotExist:
            tasks = Task.objects.none() # @@@ or throw 404?
    
    if task_filter is not None:
        # Django will not merge queries that are both not distinct or distinct
        tasks = tasks.distinct() & task_filter.qs
    
    group_by_querydict = request.GET.copy()
    group_by_querydict.pop("group_by", None)
    group_by_querystring = group_by_querydict.urlencode()
    
    return render_to_response(template_name, {
        "group": group,
        "task_filter": task_filter,
        "tasks": tasks,
        "field": field,
        "value": value,
        "group_by": group_by,
        "gbqs": group_by_querystring,
        "is_member": is_member,
        "group_base": group_base,
    }, context_instance=RequestContext(request))


def tasks_history_list(request, group_slug=None, template_name="tasks/tasks_history_list.html", bridge=None):
    
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
        tasks = group.content_objects(TaskHistory)
        group_base = bridge.group_base_template()
    else:
        tasks = TaskHistory.objects.filter(object_id=None)
        group_base = None
    tasks = tasks.order_by("-modified")
    
    return render_to_response(template_name, {
        "group": group,
        "task_history": tasks,
        "is_member": is_member,
        "group_base": group_base,
    }, context_instance=RequestContext(request))


def tasks_history(request, id, group_slug=None, template_name="tasks/task_history.html", bridge=None):
    
    if bridge:
        try:
            group = bridge.get_group(group_slug)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None
    
    if group:
        tasks = group.content_objects(Task)
        group_base = bridge.group_base_template()
    else:
        tasks = Task.objects.filter(object_id=None)
        group_base = None
    
    task = get_object_or_404(tasks, id=id)
    task_history = task.history_task.all().order_by('-modified')
    nudge_history = task.task_nudge.all().order_by('-modified')
    
    result_list = sorted(
        chain(task_history, nudge_history),
        key=attrgetter('modified')
        )
    result_list.reverse()
    
    for change in task_history:
        change.humanized_state = workflow.STATE_CHOICES_DICT.get(change.state, None)
        change.humanized_resolution = workflow.RESOLUTION_CHOICES_DICT.get(change.resolution, None)
    
    return render_to_response(template_name, {
        "group": group,
        "task": task,
        "task_history": result_list,
        "nudge_history": nudge_history,
        "group_base": group_base,
    }, context_instance=RequestContext(request))


def export_state_transitions(request):
    export = workflow.export_state_transitions()
    return HttpResponse(export, mimetype='text/csv')
