from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic import date_based

from blog.models import Post
from blog.forms import *
import datetime

try:
    from notification import models as notification
except ImportError:
    notification = None

def blogs(request):
    blogs = Post.objects.filter(status=2).order_by("-publish")
    return render_to_response("blog/blogs.html", {"blogs": blogs}, context_instance=RequestContext(request))
    
def article(request, username, month, year, slug):
    post = Post.objects.filter(slug=slug, 
                            publish__year = int(year), 
                            publish__month = int(month)).filter(author__username=username)
    if not post:
        raise Http404
    
    return render_to_response("blog/article.html", {
                        "post": post[0]}, context_instance=RequestContext(request))

def yourarticles(request):
    user = request.user
    blogs = Post.objects.filter(author=user)
    return render_to_response("blog/yourarticles.html", {"blogs": blogs}, context_instance=RequestContext(request))

@login_required
def new(request):
    if request.user.is_authenticated() and request.method == "POST":
        if request.POST["action"] == "create":
            blog_form = BlogForm(request.POST)
            if blog_form.is_valid():
                blog = blog_form.save(commit=False)
                blog.author = request.user
                blog.creator_ip = request.META['REMOTE_ADDR']
                blog.save()
                request.user.message_set.create(message="Successfully saved article '%s'" % blog.title)
                return HttpResponseRedirect(reverse("your_articles"))
        else:
            blog_form = BlogForm()
    else:
        blog_form = BlogForm()
    return render_to_response("blog/new.html", {
                        "blog_form": blog_form,
                        }, context_instance=RequestContext(request))

def edit(request, id):
    if request.user.is_authenticated() and request.method == "POST":
        post = get_object_or_404(Post, id=id)
        if request.POST["action"] == "update":
            blog_form = BlogForm(request.POST, instance=post)
            blog = blog_form.save(commit=False)
            blog.save()
            request.user.message_set.create(message="Successfully updated article '%s'" % blog.title)
            return HttpResponseRedirect(reverse("your_articles"))
        else:
            blog_form = BlogForm(instance=post)
    else:
        post = get_object_or_404(Post, id=id)
        if post.author == request.user:
            is_author = True
        else:
            is_author = False
    
    blog_form = BlogForm(instance=post)
    return render_to_response("blog/edit.html", {"is_author": is_author, "blog_form": blog_form}, context_instance=RequestContext(request))