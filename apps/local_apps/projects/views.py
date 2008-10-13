from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404

from django.core.urlresolvers import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from projects.models import Project
from projects.forms import *

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

# from zwitschern.models import TweetInstance


def create(request, form_class=ProjectForm,
        template_name="projects/create.html"):
    if request.user.is_authenticated() and request.method == "POST":
        if request.POST["action"] == "create":
            project_form = form_class(request.POST)
            if project_form.is_valid():
                project = project_form.save(commit=False)
                project.creator = request.user
                project.save()
                project_member = ProjectMember(project=project, user=request.user)
                project.members.add(project_member)
                project_member.save()
                project_form = form_class()
                return HttpResponseRedirect(project.get_absolute_url())
        else:
            project_form = form_class()
    else:
        project_form = form_class()

    return render_to_response(template_name, {
        "project_form": project_form,
    }, context_instance=RequestContext(request))


def delete(request, slug, redirect_url=None):
    project = get_object_or_404(Project, slug=slug)
    if not redirect_url:
        redirect_url = "/projects/" # @@@ can't use reverse("projects") -- what is URL name using things?
    
    if request.user.is_authenticated() and request.method == "POST" and request.user == project.creator:
        project.deleted = True
        project.save()
        request.user.message_set.create(message="Project %s deleted." % project)
        if notification:
            notification.send(project.member_users.all(), "projects_deleted", {"project": project})
    
    return HttpResponseRedirect(redirect_url)


def your_projects(request, template_name="projects/your_projects.html"):
    return render_to_response(template_name, {
        "projects": Project.objects.filter(deleted=False, members__user=request.user).order_by("name"),
    }, context_instance=RequestContext(request))
your_projects = login_required(your_projects)

def project(request, slug, template_name="projects/project.html"):
    project = get_object_or_404(Project, slug=slug)
    
    if project.deleted:
        raise Http404
    
    photos = project.photos.all()
    
    if request.user.is_authenticated() and request.method == "POST" and request.user == project.creator:
        if request.POST["action"] == "update":
            adduser_form = AddUserForm(project=project)
            project_form = ProjectUpdateForm(request.POST, instance=project)
            if project_form.is_valid():
                project = project_form.save()
        elif request.POST["action"] == "add":
            project_form = ProjectUpdateForm(instance=project)
            adduser_form = AddUserForm(project, request.POST)
            if adduser_form.is_valid():
                adduser_form.save(project, request.user)
                adduser_form = AddUserForm(project=project) # @@@ is this the right way to clear it?
        else:
            project_form = ProjectUpdateForm(instance=project)
            adduser_form = AddUserForm(project=project)
    else:
        adduser_form = AddUserForm(project=project)
        project_form = ProjectUpdateForm(instance=project)
    
    topics = project.topics.all()[:5]
    articles = Article.objects.filter(
        content_type=get_ct(project),
        object_id=project.id).order_by('-last_update')
    total_articles = articles.count()
    articles = articles[:5]
    
    total_tasks = project.tasks.count()
    tasks = project.tasks.order_by("-modified")[:10]

    # tweets = TweetInstance.objects.tweets_for(project).order_by("-sent")

    are_member = project.has_member(request.user)

    return render_to_response(template_name, {
        "project_form": project_form,
        "adduser_form": adduser_form,
        "project": project,
        "photos": photos,
        "topics": topics,
        "articles": articles,
        "total_tasks": total_tasks,
        "tasks": tasks,
        "total_articles": total_articles,
        "are_member": are_member,
    }, context_instance=RequestContext(request))

def topics(request, slug, form_class=TopicForm,
        template_name="projects/topics.html"):
    project = get_object_or_404(Project, slug=slug)
    
    if project.deleted:
        raise Http404
    
    is_member = project.has_member(request.user)
    
    if request.method == "POST":
        if is_member:
            topic_form = form_class(request.POST)
            if topic_form.is_valid():
                topic = topic_form.save(commit=False)
                topic.project = project
                topic.creator = request.user
                topic.save()
                request.user.message_set.create(message="You have started the topic %s" % topic.title)
                if notification:
                    notification.send(project.member_users.all(), "projects_new_topic", {"creator": request.user, "topic": topic, "project": project})
                topic_form = form_class() # @@@ is this the right way to reset it?
        else:
            request.user.message_set.create(message="You are not a member and so cannot start a new topic")
            topic_form = form_class()
    else:
        topic_form = form_class()

    return render_to_response(template_name, {
        "project": project,
        "is_member": is_member,
        "topic_form": topic_form,
    }, context_instance=RequestContext(request))

def topic(request, id, template_name="projects/topic.html"):
    topic = get_object_or_404(Topic, id=id)
    
    if topic.project.deleted:
        raise Http404
    
    return render_to_response(template_name, {
        'topic': topic,
    }, context_instance=RequestContext(request))

def tasks(request, slug, form_class=TaskForm,
        template_name="projects/tasks.html"):
    project = get_object_or_404(Project, slug=slug)
    
    if project.deleted:
        raise Http404
    
    is_member = project.has_member(request.user)
    
    if request.user.is_authenticated() and request.method == "POST":
        if request.POST["action"] == "add_task":
            task_form = form_class(project, request.POST)
            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.creator = request.user
                task.project = project
                # @@@ we should check that assignee is really a member
                task.save()
                request.user.message_set.create(message="added task '%s'" % task.summary)
                if notification:
                    notification.send(project.member_users.all(), "projects_new_task", {"creator": request.user, "task": task, "project": project})
                task_form = form_class(project=project) # @@@ is this the right way to clear it?
        else:
            task_form = form_class(project=project)
    else:
        task_form = form_class(project=project)
    
    group_by = request.GET.get("group_by")
    tasks = project.tasks.all()
    
    return render_to_response(template_name, {
        "project": project,
        "tasks": tasks,
        "group_by": group_by,
        "is_member": is_member,
        "task_form": task_form,
    }, context_instance=RequestContext(request))

def task(request, id, template_name="projects/task.html"):
    task = get_object_or_404(Task, id=id)
    project = task.project
    
    if project.deleted:
        raise Http404
    
    is_member = project.has_member(request.user)
    
    if is_member and request.method == "POST":
        if request.POST["action"] == "assign":
            status_form = StatusForm(instance=task)
            assign_form = AssignForm(project, request.POST, instance=task)
            if assign_form.is_valid():
                task = assign_form.save()
                request.user.message_set.create(message="assigned task to '%s'" % task.assignee)
                if notification:
                    notification.send(project.member_users.all(), "projects_task_assignment", {"user": request.user, "task": task, "project": project, "assignee": task.assignee})
        elif request.POST["action"] == "update_status":
            assign_form = AssignForm(project, instance=task)
            status_form = StatusForm(request.POST, instance=task)
            if status_form.is_valid():
                task = status_form.save()
                request.user.message_set.create(message="updated your status on the task")
                if notification:
                    notification.send(project.member_users.all(), "projects_task_status", {"user": request.user, "task": task, "project": project})
        else:
            assign_form = AssignForm(project, instance=task)
            status_form = StatusForm(instance=task)
            if request.POST["action"] == "mark_resolved" and request.user == task.assignee:
                task.state = '2'
                task.save()
                request.user.message_set.create(message="task marked resolved")
                if notification:
                    notification.send(project.member_users.all(), "projects_task_change", {"user": request.user, "task": task, "project": project, "new_state": "resolved"})
            elif request.POST["action"] == "mark_closed" and request.user == task.creator:
                task.state = '3'
                task.save()
                request.user.message_set.create(message="task marked closed")
                if notification:
                    notification.send(project.member_users.all(), "projects_task_change", {"user": request.user, "task": task, "project": project, "new_state": "closed"})
            elif request.POST["action"] == "reopen" and is_member:
                task.state = '1'
                task.save()
                request.user.message_set.create(message="task reopened")
                if notification:
                    notification.send(project.member_users.all(), "projects_task_change", {"user": request.user, "task": task, "project": project, "new_state": "reopened"})
    else:
        assign_form = AssignForm(project, instance=task)
        status_form = StatusForm(instance=task)
    
    return render_to_response(template_name, {
        "task": task,
        "is_member": is_member,
        "assign_form": assign_form,
        "status_form": status_form,
    }, context_instance=RequestContext(request))

def user_tasks(request, username, template_name="projects/user_tasks.html"):
    other_user = get_object_or_404(User, username=username)
    tasks = other_user.assigned_project_tasks.filter(project__deleted=False).order_by("state")

    return render_to_response(template_name, {
        "tasks": tasks,
        "other_user": other_user,
    }, context_instance=RequestContext(request))
user_tasks = login_required(user_tasks)

def members_status(request, slug, form_class=AwayForm,
        template_name="projects/members_status.html"):
    project = get_object_or_404(Project, slug=slug)
    
    if project.deleted:
        raise Http404
    
    is_member = project.has_member(request.user)
    try:
        project_member = project.members.get(user=request.user)
    except ProjectMember.DoesNotExist:
        project_member = None
    
    away_form = None
    if is_member and request.method == "POST":
        if request.POST["action"] == "set_away":
            away_form = form_class(request.POST)
            if away_form.is_valid():
                away_form.save(project_member)
                away_form = form_class()
        elif request.POST["action"] == "set_back":
            project_member.away = False
            project_member.save()
    
    if away_form is None:
        away_form = form_class()
    
    active_members = project.members.filter(away=False)
    away_members = project.members.filter(away=True).order_by('away_since')
    
    return render_to_response(template_name, {
        "project": project,
        "is_member": is_member,
        "project_member": project_member,
        "away_form": away_form,
        "active_members": active_members,
        "away_members": away_members,
    }, context_instance=RequestContext(request))
members_status = login_required(members_status)
