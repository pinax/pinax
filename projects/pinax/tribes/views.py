from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from django.contrib.auth.models import User
from tribes.models import Tribe
from tribes.forms import TribeForm, TribeUpdateForm

try:
    from notification import models as notification
except ImportError:
    notification = None


def tribes(request):
    if request.user.is_authenticated() and request.method == "POST":
        if request.POST["action"] == "create":
            tribe_form = TribeForm(request.POST)
            if tribe_form.is_valid():
                tribe = tribe_form.save(commit=False)
                tribe.creator = request.user
                tribe.save()
                tribe.members.add(request.user)
                tribe.save()
                tribe_form = TribeForm()
                
        else:
            tribe_form = TribeForm()
    else:
        tribe_form = TribeForm()
    
    return render_to_response("tribes/tribes.html", {
        "tribe_form": tribe_form,
        "tribes": Tribe.objects.all().order_by("-created"),
    }, context_instance=RequestContext(request))

def tribe(request, slug):
    tribe = get_object_or_404(Tribe, slug=slug)
    
    if request.user.is_authenticated() and request.method == "POST":
        if request.POST["action"] == "update" and request.user == tribe.creator:
            tribe_form = TribeUpdateForm(request.POST, instance=tribe)
            if tribe_form.is_valid():
                tribe = tribe_form.save()
        if request.POST["action"] == "join":
            tribe.members.add(request.user)
            request.user.message_set.create(message="You have joined the tribe %s" % tribe.name)
            if notification:
                pass # @@@
        elif request.POST["action"] == "leave":
            tribe.members.remove(request.user)
            request.user.message_set.create(message="You have left the tribe %s" % tribe.name)
            if notification:
                pass # @@@
    
    tribe_form = TribeUpdateForm(instance=tribe)
    
    are_member = request.user in tribe.members.all()
    
    return render_to_response("tribes/tribe.html", {
        "tribe_form": tribe_form,
        "tribe": tribe,
        "are_member": are_member,
    }, context_instance=RequestContext(request))
    