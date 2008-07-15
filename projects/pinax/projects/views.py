from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

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


def projects(request):
    if request.user.is_authenticated() and request.method == "POST":
        if request.POST["action"] == "create":
            project_form = ProjectForm(request.POST)
            if project_form.is_valid():
                project = project_form.save(commit=False)
                project.creator = request.user
                project.save()
                project.members.add(request.user)
                project.save()
                project_form = ProjectForm()
        else:
            project_form = ProjectForm()
    else:
        project_form = ProjectForm()

    return render_to_response("projects/projects.html", {
        "project_form": project_form,
        "projects": Project.objects.all().order_by("-created"),
    }, context_instance=RequestContext(request))

@login_required
def your_projects(request):
    return render_to_response("projects/your_projects.html", {
        "projects": Project.objects.filter(members=request.user).order_by("name"),
    }, context_instance=RequestContext(request))

def project(request, slug):
    project = get_object_or_404(Project, slug=slug)

    if request.user.is_authenticated() and request.method == "POST" and request.user == project.creator:
        if request.POST["action"] == "update":
            adduser_form = AddUserForm()
            project_form = ProjectUpdateForm(request.POST, instance=project)
            if project_form.is_valid():
                project = project_form.save()
        elif request.POST["action"] == "add":
            project_form = ProjectUpdateForm(instance=project)
            adduser_form = AddUserForm(request.POST)
            if adduser_form.is_valid():
                adduser_form.save(project, request.user)
                adduser_form = AddUserForm() # @@@ is this the right way to clear it?
        else:
            project_form = ProjectUpdateForm(instance=project)
            adduser_form = AddUserForm()
    else:
        adduser_form = AddUserForm()
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

    are_member = request.user in project.members.all()

    return render_to_response("projects/project.html", {
        "project_form": project_form,
        "adduser_form": adduser_form,
        "project": project,
        "topics": topics,
        "articles": articles,
        "total_tasks": total_tasks,
        "tasks": tasks,
        "total_articles": total_articles,
        "are_member": are_member,
    }, context_instance=RequestContext(request))

def topics(request, slug):
    project = get_object_or_404(Project, slug=slug)
    is_member = request.user.is_authenticated() and request.user in project.members.all()

    if request.method == "POST":
        if is_member:
            topic_form = TopicForm(request.POST)
            if topic_form.is_valid():
                topic = topic_form.save(commit=False)
                topic.project = project
                topic.creator = request.user
                topic.save()
                request.user.message_set.create(message="You have started the topic %s" % topic.title)
                if notification:
                    notification.send(project.members.all(), "projects_new_topic", {"creator": request.user, "topic": topic, "project": project})
                topic_form = TopicForm() # @@@ is this the right way to reset it?
        else:
            request.user.message_set.create(message="You are not a member and so cannot start a new topic")
            topic_form = TopicForm()
    else:
        topic_form = TopicForm()

    return render_to_response("projects/topics.html", {
        "project": project,
        "is_member": is_member,
        "topic_form": topic_form,
    }, context_instance=RequestContext(request))


def topic(request, id):
    topic = get_object_or_404(Topic, id=id)

    return render_to_response("projects/topic.html", {
        'topic': topic,
    }, context_instance=RequestContext(request))

def tasks(request, slug):
    project = get_object_or_404(Project, slug=slug)
    is_member = request.user.is_authenticated() and request.user in project.members.all()

    if request.user.is_authenticated() and request.method == "POST":
        if request.POST["action"] == "add_task":
            task_form = TaskForm(project, request.POST)
            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.creator = request.user
                task.project = project
                # @@@ we should check that assignee is really a member
                task.save()
                request.user.message_set.create(message="added task '%s'" % task.summary)
                if notification:
                    notification.send(project.members.all(), "projects_new_task", {"creator": request.user, "task": task, "project": project})
                task_form = TaskForm(project=project) # @@@ is this the right way to clear it?
        else:
            task_form = TaskForm(project=project)
    else:
        task_form = TaskForm(project=project)

    group_by = request.GET.get("group_by")
    tasks = project.tasks.all()

    return render_to_response("projects/tasks.html", {
        "project": project,
        "tasks": tasks,
        "group_by": group_by,
        "is_member": is_member,
        "task_form": task_form,
    }, context_instance=RequestContext(request))

def task(request, id):
    task = get_object_or_404(Task, id=id)
    project = task.project
    is_member = request.user.is_authenticated() and request.user in project.members.all()

    if is_member and request.method == "POST":
        if request.POST["action"] == "assign":
            status_form = StatusForm(instance=task)
            assign_form = AssignForm(project, request.POST, instance=task)
            if assign_form.is_valid():
                task = assign_form.save()
                request.user.message_set.create(message="assigned task to '%s'" % task.assignee)
                if notification:
                    notification.send(project.members.all(), "projects_task_assignment", {"user": request.user, "task": task, "project": project, "assignee": task.assignee})
        elif request.POST["action"] == "update_status":
            assign_form = AssignForm(project, instance=task)
            status_form = StatusForm(request.POST, instance=task)
            if status_form.is_valid():
                task = status_form.save()
                request.user.message_set.create(message="updated your status on the task")
                if notification:
                    notification.send(project.members.all(), "projects_task_status", {"user": request.user, "task": task, "project": project})
        else:
            assign_form = AssignForm(project, instance=task)
            status_form = StatusForm(instance=task)
            if request.POST["action"] == "mark_resolved" and request.user == task.assignee:
                task.state = '2'
                task.save()
                request.user.message_set.create(message="task marked resolved")
                if notification:
                    notification.send(project.members.all(), "projects_task_change", {"user": request.user, "task": task, "project": project, "new_state": "resolved"})
            elif request.POST["action"] == "mark_closed" and request.user == task.creator:
                task.state = '3'
                task.save()
                request.user.message_set.create(message="task marked closed")
                if notification:
                    notification.send(project.members.all(), "projects_task_change", {"user": request.user, "task": task, "project": project, "new_state": "closed"})
            elif request.POST["action"] == "reopen" and is_member:
                task.state = '1'
                task.save()
                request.user.message_set.create(message="task reopened")
                if notification:
                    notification.send(project.members.all(), "projects_task_change", {"user": request.user, "task": task, "project": project, "new_state": "reopened"})
    else:
        assign_form = AssignForm(project, instance=task)
        status_form = StatusForm(instance=task)

    return render_to_response("projects/task.html", {
        "task": task,
        "is_member": is_member,
        "assign_form": assign_form,
        "status_form": status_form,
    }, context_instance=RequestContext(request))

@login_required
def user_tasks(request, username):
    other_user = get_object_or_404(User, username=username)
    tasks = other_user.assigned_project_tasks.order_by("state")

    return render_to_response("projects/user_tasks.html", {
        "tasks": tasks,
        "other_user": other_user,
    }, context_instance=RequestContext(request))
