from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic import date_based
from django.conf import settings

from blog.models import Post
from blog.forms import *
import datetime

try:
    from notification import models as notification
except ImportError:
    notification = None

try:
    from friends.models import Friendship
    friends = True
except ImportError:
    friends = False

def blogs(request, username=None, template_name="blog/blogs.html"):
    blogs = Post.objects.filter(status=2).select_related(depth=1).order_by("-publish")
    if username is not None:
        user = get_object_or_404(User, username=username.lower())
        blogs = blogs.filter(author=user)
    return render_to_response(template_name, {
        "blogs": blogs,
    }, context_instance=RequestContext(request))

def post(request, username, year, month, slug,
         template_name="blog/post.html"):
    post = Post.objects.filter(slug=slug, publish__year=int(year), publish__month=int(month)).filter(author__username=username)
    if not post:
        raise Http404

    if post[0].status == 1 and post[0].author != request.user:
        raise Http404

    return render_to_response(template_name, {
        "post": post[0],
    }, context_instance=RequestContext(request))

def your_posts(request, template_name="blog/your_posts.html"):
    return render_to_response(template_name, {
        "blogs": Post.objects.filter(author=request.user),
    }, context_instance=RequestContext(request))
your_posts = login_required(your_posts)

def destroy(request, id):
    post = Post.objects.get(pk=id)
    user = request.user
    title = post.title
    if post.author != request.user:
            request.user.message_set.create(message="You can't delete posts that aren't yours")
            return HttpResponseRedirect(reverse("blog_list_yours"))

    if request.method == "POST" and request.POST["action"] == "delete":
        post.delete()
        request.user.message_set.create(message=_("Successfully deleted post '%s'") % title)
        return HttpResponseRedirect(reverse("blog_list_yours"))
    else:
        return HttpResponseRedirect(reverse("blog_list_yours"))

    return render_to_response(context_instance=RequestContext(request))
destroy = login_required(destroy)

def new(request, form_class=BlogForm, template_name="blog/new.html"):
    if request.method == "POST":
        if request.POST["action"] == "create":
            blog_form = form_class(request.user, request.POST)
            if blog_form.is_valid():
                blog = blog_form.save(commit=False)
                blog.author = request.user
                if settings.BEHIND_PROXY:
                    blog.creator_ip = request.META["HTTP_X_FORWARDED_FOR"]
                else:
                    blog.creator_ip = request.META['REMOTE_ADDR']
                blog.save()
                # @@@ should message be different if published?
                request.user.message_set.create(message=_("Successfully saved post '%s'") % blog.title)
                if notification:
                    if blog.status == 2: # published
                        if friends: # @@@ might be worth having a shortcut for sending to all friends
                            notification.send((x['friend'] for x in Friendship.objects.friends_for_user(blog.author)), "blog_friend_post", {"post": blog})
                
                return HttpResponseRedirect(reverse("blog_list_yours"))
        else:
            blog_form = form_class()
    else:
        blog_form = form_class()

    return render_to_response(template_name, {
        "blog_form": blog_form
    }, context_instance=RequestContext(request))
new = login_required(new)

def edit(request, id, form_class=BlogForm, template_name="blog/edit.html"):
    post = get_object_or_404(Post, id=id)

    if request.method == "POST":
        if post.author != request.user:
            request.user.message_set.create(message="You can't edit posts that aren't yours")
            return HttpResponseRedirect(reverse("blog_list_yours"))
        if request.POST["action"] == "update":
            blog_form = form_class(request.user, request.POST, instance=post)
            if blog_form.is_valid():
                blog = blog_form.save(commit=False)
                blog.save()
                request.user.message_set.create(message=_("Successfully updated post '%s'") % blog.title)
                if notification:
                    if blog.status == 2: # published
                        if friends: # @@@ might be worth having a shortcut for sending to all friends
                            notification.send((x['friend'] for x in Friendship.objects.friends_for_user(blog.author)), "blog_friend_post", {"post": blog})
                
                return HttpResponseRedirect(reverse("blog_list_yours"))
        else:
            blog_form = form_class(instance=post)
    else:
        blog_form = form_class(instance=post)

    return render_to_response(template_name, {
        "blog_form": blog_form,
        "post": post,
    }, context_instance=RequestContext(request))
edit = login_required(edit)
