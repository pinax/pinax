from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404, get_host
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic import date_based
from django.conf import settings

from photos.models import *
from photos.forms import *
from projects.models import *
from tribes.models import *
import datetime

@login_required
def upload(request):
    """upload form for photos"""
    photo_form = PhotoUploadForm()
    if request.method == 'POST':
        if request.POST["action"] == "upload":
            photo_form = PhotoUploadForm(request.user, request.POST, request.FILES)
            if photo_form.is_valid():
                photo = photo_form.save(commit=False)
                photo.member = request.user
                photo.save()
                request.user.message_set.create(message=_("Successfully uploaded photo '%s'") % photo.title)
                return HttpResponseRedirect(reverse("photo_upload"))

    return render_to_response("photos/upload.html", {"photo_form": photo_form}, context_instance=RequestContext(request))

@login_required
def yourphotos(request):
    '''photos for the currently authenticated user'''
    user = request.user
    photos = Photos.objects.filter(member=user).order_by("-date_added")
    return render_to_response("photos/yourphotos.html", {"photos": photos}, context_instance=RequestContext(request))

@login_required    
def photos(request):
    '''latest photos'''
    photos = Photos.objects.filter(is_public=True).order_by("-date_added")
    return render_to_response("photos/latest.html", {"photos": photos}, context_instance=RequestContext(request))

@login_required
def details(request, id):
    '''show the photo details'''
    other_user = get_object_or_404(User, username=request.user.username)
    tribes = Tribe.objects.filter(members=request.user)
    projects = Project.objects.filter(members=request.user)
    photo = get_object_or_404(Photos, id=id)
    title = photo.title
    host = "http://%s" % get_host(request)
    if photo.member == request.user:
        is_me = True
    else:
        is_me = False
    # TODO: check for authorized user and catch errors
    if photo.member == request.user:
        if request.method == "POST" and request.POST["action"] == "add_to_project":
            projectid = request.POST["project"]
            myproject = Project.objects.get(pk=projectid)
            myproject.photos.create(photo=photo)
            request.user.message_set.create(message=_("Successfully add photo '%s' to project") % title)
            # TODO: figure out why reverse doesn't work and redo this
            return render_to_response("photos/details.html", {
                      "host": host, 
                      "photo": photo, 
                      "is_me": is_me, 
                      "other_user": other_user, 
                      "projects": projects,
                      "tribes": tribes}, context_instance=RequestContext(request))
        
        if request.method == "POST" and request.POST["action"] == "add_to_tribe":
            tribeid = request.POST["tribe"]
            mytribe = Tribe.objects.get(pk=tribeid)
            mytribe.photos.create(photo=photo)
            request.user.message_set.create(message=_("Successfully add photo '%s' to tribe") % title)
            # TODO: figure out why reverse doesn't work and redo this
            return render_to_response("photos/details.html", {
                      "host": host, 
                      "photo": photo, 
                      "is_me": is_me, 
                      "other_user": other_user, 
                      "projects": projects,
                      "tribes": tribes}, context_instance=RequestContext(request))


    return render_to_response("photos/details.html", {
                      "host": host, 
                      "photo": photo, 
                      "is_me": is_me, 
                      "other_user": other_user, 
                      "projects": projects,
                      "tribes": tribes
                      }, context_instance=RequestContext(request))
    
@login_required
def memberphotos(request, username):
    '''Get the members photos and display them'''
    user = get_object_or_404(User, username=username)
    photos = Photos.objects.filter(member__username=username,is_public=True).order_by("-date_added")
    return render_to_response("photos/memberphotos.html", {"photos": photos}, context_instance=RequestContext(request))

@login_required
def destroy(request, id):
    photo = Photos.objects.get(pk=id)
    user = request.user
    title = photo.title
    if photo.member != request.user:
            request.user.message_set.create(message="You can't delete photos that aren't yours")
            return HttpResponseRedirect(reverse("photos_yours"))

    if request.method == "POST" and request.POST["action"] == "delete":
        photo.delete()
        request.user.message_set.create(message=_("Successfully deleted photo '%s'") % title)
        return HttpResponseRedirect(reverse("photos_yours"))
    else:
        return HttpResponseRedirect(reverse("photos_yours"))

@login_required
def addproject(request, project):
    photo = get_object_or_404(Photos, id=id)
    title = photo.title
    project = Project.objects.get(pk=tribe)
    pool = Pool(content_type=photo)
    pool.save()
    request.user.message_set.create(message=_("Successfully add photo '%s' to tribe") % title)
    return HttpResponseRedirect(reverse("photos_yours", photo))
