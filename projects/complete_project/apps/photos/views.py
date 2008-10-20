from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, get_host
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from photologue.models import *
from photos.models import Image
from photos.forms import PhotoUploadForm, PhotoEditForm
from projects.models import Project
from tribes.models import Tribe

def upload(request, form_class=PhotoUploadForm,
        template_name="photos/upload.html"):
    """
    upload form for photos
    """
    photo_form = form_class()
    if request.method == 'POST':
        if request.POST["action"] == "upload":
            photo_form = form_class(request.user, request.POST, request.FILES)
            if photo_form.is_valid():
                photo = photo_form.save(commit=False)
                photo.member = request.user
                photo.save()
                request.user.message_set.create(message=_("Successfully uploaded photo '%s'") % photo.title)
                return HttpResponseRedirect(reverse('photo_details', args=(photo.id,)))

    return render_to_response(template_name, {
        "photo_form": photo_form,
    }, context_instance=RequestContext(request))
upload = login_required(upload)

def yourphotos(request, template_name="photos/yourphotos.html"):
    """
    photos for the currently authenticated user
    """
    photos = Image.objects.filter(member=request.user).order_by("-date_added")
    return render_to_response(template_name, {
        "photos": photos,
    }, context_instance=RequestContext(request))
yourphotos = login_required(yourphotos)

def photos(request, template_name="photos/latest.html"):
    """
    latest photos
    """
    photos = Image.objects.filter(is_public=True).order_by("-date_added")
    return render_to_response(template_name, {
        "photos": photos,
    }, context_instance=RequestContext(request))
photos = login_required(photos)

def details(request, id, template_name="photos/details.html"):
    """
    show the photo details
    """
    other_user = get_object_or_404(User, username=request.user.username)
    tribes = Tribe.objects.filter(members=request.user)
    projects = Project.objects.filter(members__user=request.user)
    photo = get_object_or_404(Image, id=id)
    photo_url = photo.get_display_url()
    
    # Build a list of tribes and the photos from the pool
    t = []
    if tribes:
        for tribe in tribes:
            phototribe = Tribe.objects.get(pk=tribe.id)
            if phototribe.photos.filter(photo=photo).count():
                t.append({"name":tribe.name, "slug":tribe.slug, "id":tribe.id, "has_photo":True})
            else:
                t.append({"name":tribe.name, "slug":tribe.slug, "id":tribe.id, "has_photo":False})

    # Build a list of projects and the photos from the pool
    p = []
    if projects:
        for project in projects:
            photoproject = Project.objects.get(pk=project.id)
            if photoproject.photos.filter(photo=photo).count():
                p.append({"name":project.name, "slug":project.slug, "id":project.id, "has_photo":True})
            else:
                p.append({"name":project.name, "slug":project.slug, "id":project.id, "has_photo":False})


    title = photo.title
    host = "http://%s" % get_host(request)
    if photo.member == request.user:
        is_me = True
    else:
        is_me = False
    # TODO: check for authorized user and catch errors
    if is_me:
        if request.method == "POST" and request.POST["action"] == "add_to_project":
            projectid = request.POST["project"]
            myproject = Project.objects.get(pk=projectid)
            if not myproject.photos.filter(photo=photo).count():
                myproject.photos.create(photo=photo)
                request.user.message_set.create(message=_("Successfully add photo '%s' to project") % title)
            else:
                # TODO: this applies to pinax in general. dont use ugettext_lazy here. its usage is fragile.
                request.user.message_set.create(message=_("Did not add photo '%s' to project because it already exists.") % title)

            return HttpResponseRedirect(reverse('photo_details', args=(photo.id,)))
        
        if request.method == "POST":
            if request.POST["action"] == "addtotribe":
                tribeid = request.POST["tribe"]
                mytribe = Tribe.objects.get(pk=tribeid)
                if not mytribe.photos.filter(photo=photo).count():
                    mytribe.photos.create(photo=photo)
                    request.user.message_set.create(message=_("Successfully add photo '%s' to tribe") % title)
                else:
                    # TODO: this applies to pinax in general. dont use ugettext_lazy here. its usage is fragile.
                    request.user.message_set.create(message=_("Did not add photo '%s' to tribe because it already exists.") % title)

                return HttpResponseRedirect(reverse('photo_details', args=(photo.id,)))

            if request.POST["action"] == "removefromtribe":
                tribeid = request.POST["tribe"]
                mytribe = Tribe.objects.get(pk=tribeid)
                if mytribe.photos.filter(photo=photo).count():
                    mytribe.photos.filter(photo=photo).delete()
                    request.user.message_set.create(message=_("Successfully removed photo '%s' from tribe") % title)
                else:
                    # TODO: this applies to pinax in general. dont use ugettext_lazy here. its usage is fragile.
                    request.user.message_set.create(message=_("Did not remove photo '%s' from tribe.") % title)

                return HttpResponseRedirect(reverse('photo_details', args=(photo.id,)))

            if request.POST["action"] == "addtoproject":
                projectid = request.POST["project"]
                myproject = Project.objects.get(pk=projectid)
                if not myproject.photos.filter(photo=photo).count():
                    myproject.photos.create(photo=photo)
                    request.user.message_set.create(message=_("Successfully add photo '%s' to project") % title)
                else:
                    # TODO: this applies to pinax in general. dont use ugettext_lazy here. its usage is fragile.
                    request.user.message_set.create(message=_("Did not add photo '%s' to project because it already exists.") % title)

                return HttpResponseRedirect(reverse('photo_details', args=(photo.id,)))

            if request.POST["action"] == "removefromproject":
                projectid = request.POST["project"]
                myproject = Project.objects.get(pk=projectid)
                if myproject.photos.filter(photo=photo).count():
                    myproject.photos.filter(photo=photo).delete()
                    request.user.message_set.create(message=_("Successfully removed photo '%s' from project") % title)
                else:
                    # TODO: this applies to pinax in general. dont use ugettext_lazy here. its usage is fragile.
                    request.user.message_set.create(message=_("Did not remove photo '%s' from project.") % title)

                return HttpResponseRedirect(reverse('photo_details', args=(photo.id,)))

    return render_to_response(template_name, {
        "host": host, 
        "photo": photo,
        "photo_url": photo_url,
        "is_me": is_me, 
        "other_user": other_user, 
        "projects": p,
        "tribes": t,
    }, context_instance=RequestContext(request))
details = login_required(details)

def memberphotos(request, username, template_name="photos/memberphotos.html"):
    """
    Get the members photos and display them
    """
    user = get_object_or_404(User, username=username)
    photos = Image.objects.filter(member__username=username, is_public=True).order_by("-date_added")
    return render_to_response(template_name, {
        "photos": photos,
    }, context_instance=RequestContext(request))
memberphotos = login_required(memberphotos)

def edit(request, id, form_class=PhotoEditForm,
        template_name="photos/edit.html"):
    photo = get_object_or_404(Image, id=id)
    photo_url = photo.get_display_url()

    if request.method == "POST":
        if photo.member != request.user:
            request.user.message_set.create(message="You can't edit photos that aren't yours")
            return HttpResponseRedirect(reverse('photo_details', args=(photo.id,)))
        if request.POST["action"] == "update":
            photo_form = form_class(request.user, request.POST, instance=photo)
            if photo_form.is_valid():
                photoobj = photo_form.save(commit=False)
                photoobj.save()
                request.user.message_set.create(message=_("Successfully updated photo '%s'") % photo.title)
                                
                return HttpResponseRedirect(reverse('photo_details', args=(photo.id,)))
        else:
            photo_form = form_class(instance=photo)

    else:
        photo_form = form_class(instance=photo)

    return render_to_response(template_name, {
        "photo_form": photo_form,
        "photo": photo,
        "photo_url": photo_url,
    }, context_instance=RequestContext(request))
edit = login_required(edit)

def destroy(request, id):
    photo = Image.objects.get(pk=id)
    title = photo.title
    if photo.member != request.user:
        request.user.message_set.create(message="You can't delete photos that aren't yours")
        return HttpResponseRedirect(reverse("photos_yours"))

    if request.method == "POST" and request.POST["action"] == "delete":
        photo.delete()
        request.user.message_set.create(message=_("Successfully deleted photo '%s'") % title)
    return HttpResponseRedirect(reverse("photos_yours"))
destroy = login_required(destroy)
