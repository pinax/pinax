from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from bookmarks.models import Bookmark
from bookmarks.forms import BookmarkForm

def bookmarks(request):
    bookmarks = Bookmark.objects.all().order_by("-added")

    return render_to_response("bookmarks/bookmarks.html", {
        "bookmarks": bookmarks,
    }, context_instance=RequestContext(request))

@login_required
def add(request):

    if request.method == "POST":
        bookmark_form = BookmarkForm(request.POST)
        if bookmark_form.is_valid():
            bookmark = bookmark_form.save(commit=False)
            bookmark.adder = request.user
            bookmark.save()
            return HttpResponseRedirect(reverse("bookmarks.views.bookmarks"))
    else:
        initial = {}
        if 'url' in request.GET:
            initial['url'] = request.GET["url"]
        if 'description' in request.GET:
            initial['description'] = request.GET["description"]

        if initial:
            bookmark_form = BookmarkForm(initial=initial)
        else:
            bookmark_form = BookmarkForm()

    return render_to_response("bookmarks/add.html", {
        "bookmark_form": bookmark_form,
    }, context_instance=RequestContext(request))
