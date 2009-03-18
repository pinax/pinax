from datetime import date

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_app

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from tagging.models import Tag

from tasks.models import Task
from tasks.forms import TaskForm, EditTaskForm

try:
    notification = get_app('notification')
except ImproperlyConfigured:
    notification = None


def tasks(request, group_slug=None, template_name="tasks/task_list.html"):
    group = None # get_object_or_404(Project, slug=slug)
    
    # @@@ if group.deleted:
    # @@@     raise Http404
    
    is_member = True # @@@ groups.has_member(request.user)
    
    group_by = request.GET.get("group_by")
    
    if group:
        tasks = group.tasks.all() # @@@ assumes GR
    else:
        tasks = Task.objects.filter(object_id__isnull=True)
    
    return render_to_response(template_name, {
        "group": group,
        "tasks": tasks,
        "group_by": group_by,
        "is_member": is_member,
    }, context_instance=RequestContext(request))


def add_task(request, group_slug=None, form_class=TaskForm, template_name="tasks/add.html"):
    group = None # get_object_or_404(Project, slug=slug)
    
    # @@@ if group.deleted:
    # @@@     raise Http404
    
    if group:
        notify_list = group.member_users.all() # @@@
    else:
        notify_list = User.objects.all()
    
    is_member = True # @@@ groups.has_member(request.user)
    
    if request.user.is_authenticated() and request.method == "POST":
        task_form = form_class(group, request.POST)
        if task_form.is_valid():
            task = task_form.save(commit=False)
            task.creator = request.user
            task.group = group
            # @@@ we should check that assignee is really a member
            task.save()
            request.user.message_set.create(message="added task '%s'" % task.summary)
            if notification:
                notification.send(notify_list, "tasks_new", {"creator": request.user, "task": task, "group": group})
            return HttpResponseRedirect(reverse("task_list"))
    else:
        task_form = form_class(group=group)
    
    return render_to_response(template_name, {
        "group": group,
        "is_member": is_member,
        "task_form": task_form,
    }, context_instance=RequestContext(request))


def task(request, id, template_name="tasks/task.html"):
    task = get_object_or_404(Task, id=id)
    group = task.group
    
    # @@@ if group.deleted:
    # @@@     raise Http404
    
    if group:
        notify_list = group.member_users.all() # @@@
    else:
        notify_list = User.objects.all()
    
    is_member = True # @@@ groups.has_member(request.user)
    
    if is_member and request.method == "POST":
        form = EditTaskForm(request.user, request.POST, instance=task)
        if form.is_valid():
            task = form.save()
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
            form = EditTaskForm(request.user, instance=task)
    else:
        form = EditTaskForm(request.user, instance=task)
    
    return render_to_response(template_name, {
        "task": task,
        "is_member": is_member,
        "form": form,
    }, context_instance=RequestContext(request))


@login_required
def user_tasks(request, username, template_name="tasks/user_tasks.html"):
    other_user = get_object_or_404(User, username=username)
    assigned_tasks = other_user.assigned_tasks.all().order_by("state", "-modified") # @@@ filter(project__deleted=False)
    created_tasks = other_user.created_tasks.all().order_by("state", "-modified") # @@@ filter(project__deleted=False)
    
    url = reverse("tasks_mini_list")
    
    bookmarklet = """javascript:(
            function() {
                url = '%s';
                window.open(url, 'tasklist', 'height=500, width=250, title=no, location=no, scrollbars=yes, menubars=no, navigation=no, statusbar=no, directories=no, resizable=yes, status=no, toolbar=no, menuBar=no');
            }
        )()""" % url
    
    return render_to_response(template_name, {
        "assigned_tasks": assigned_tasks,
        "created_tasks": created_tasks,
        "other_user": other_user,
        "bookmarklet": bookmarklet,
    }, context_instance=RequestContext(request))


@login_required
def mini_list(request, template_name="tasks/mini_list.html"):
    assigned_tasks = request.user.assigned_tasks.all().exclude(state="2").exclude(state="3").order_by("state", "-modified") # @@@ filter(project__deleted=False)
    return render_to_response(template_name, {
        "assigned_tasks": assigned_tasks,
    }, context_instance=RequestContext(request))


def focus(request, field, value, group_slug=None, template_name="tasks/focus.html"):
    group = None # get_object_or_404(Project, slug=slug)
    
    # @@@ if group.deleted:
    # @@@     raise Http404
    
    is_member = True # @@@ groups.has_member(request.user)
    
    group_by = request.GET.get("group_by")
    
    if group:
        qs = group.tasks.all()
    else:
        qs = Task.objects.filter(object_id__isnull=True)
    
    if field == "modified":
        try:
            # @@@ this seems hackish and brittle but I couldn't work out another way
            year, month, day = value.split("-")
            # have to int month and day in case zero-padded
            tasks = qs.filter(modified__year=int(year), modified__month=int(month), modified__day=int(day))
        except:
            tasks = Task.objects.none() # @@@ or throw 404?
    elif field == "state":
        tasks = qs.filter(state=Task.REVERSE_STATE_CHOICES[value])
    elif field == "assignee":
        if value == "unassigned": # @@@ this means can't have a username 'unassigned':
            tasks = qs.filter(assignee__isnull=True)
        else:
            try:
                assignee = User.objects.get(username=value)
                tasks = qs.filter(assignee=assignee)
            except User.DoesNotExist:
                tasks = Task.objects.none() # @@@ or throw 404?
    elif field == "tag":
        try:
            # @@@ is there a better way?
            task_type = ContentType.objects.get_for_model(Task)
            tasks = Task.objects.filter(id__in=Tag.objects.get(name=value).items.filter(content_type=task_type).values_list("object_id", flat=True))
            # @@@ still need to filter on group if group not None
        except Tag.DoesNotExist:
            tasks = Task.objects.none() # @@@ or throw 404?
    else:
        tasks = qs
        
    return render_to_response(template_name, {
        "group": group,
        "tasks": tasks,
        "field": field,
        "value": value,
        "group_by": group_by,
        "is_member": is_member,
    }, context_instance=RequestContext(request))
