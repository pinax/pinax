from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

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
    
    if request.user.is_authenticated() and request.method == "POST":
        if request.POST["action"] == "add_task":
            task_form = TaskForm(request.POST)
            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.creator = request.user
                task.project = project
                task.save()
                request.user.message_set.create(message="added task '%s'" % task.summary)
                task_form = TaskForm() # @@@ is this the right way to clear it?
        else:
            task_form = TaskForm()
    else:
        task_form = TaskForm()
    
    
    topics = project.topics.all()[:5]
    articles = Article.objects.filter(
        content_type=get_ct(project),
        object_id=project.id).order_by('-last_update')
    total_articles = articles.count()
    articles = articles[:5]
    
    # tweets = TweetInstance.objects.tweets_for(project).order_by("-sent")
    
    are_member = request.user in project.members.all()
    
    task_form = TaskForm()
    
    return render_to_response("projects/project.html", {
        "project_form": project_form,
        "adduser_form": adduser_form,
        "task_form": task_form,
        "project": project,
        "topics": topics,
        "articles": articles,
        # "tweets": tweets,
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
                    notification.send(project.members.all(), "projects_new_topic", "%(creator)s has started a topic '%(topic)s' in project %(project)s.", {"creator": request.user, "topic": topic, "project": project})
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
