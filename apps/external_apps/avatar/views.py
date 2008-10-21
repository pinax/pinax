import os
import os.path

from avatar.models import Avatar, avatar_file_path
from avatar.forms import PrimaryAvatarForm, DeleteAvatarForm
from urllib2 import urlopen
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.core.files.storage import default_storage

try:
    from PIL import ImageFile
except ImportError:
    import ImageFile
try:
    from PIL import Image
except ImportError:
    import Image

MAX_MEGABYTES = getattr(settings, 'AVATAR_MAX_FILESIZE', 10)
MAX_WIDTH = getattr(settings, 'AVATAR_MAX_WIDTH', 512)
DEFAULT_WIDTH = getattr(settings, 'AVATAR_DEFAULT_WIDTH', 80)
AVATAR_RESIZE_METHOD = getattr(settings, 'AVATAR_RESIZE_METHOD', Image.ANTIALIAS)

def _get_next(request):
    """
    The part that's the least straightforward about views in this module is how they 
    determine their redirects after they have finished computation.

    In short, they will try and determine the next place to go in the following order:

    1. If there is a variable named ``next`` in the *POST* parameters, the view will
    redirect to that variable's value.
    2. If there is a variable named ``next`` in the *GET* parameters, the view will
    redirect to that variable's value.
    3. If Django can determine the previous page from the HTTP headers, the view will
    redirect to that previous page.
    4. Otherwise, the view raise a 404 Not Found.
    """
    next = request.POST.get('next', request.GET.get('next', request.META.get('HTTP_REFERER', None)))
    #if not next or next == request.path:
    #    raise Http404 # No next url was supplied in GET or POST.
    if not next:
        next = request.path
    return next

def img(request, email_hash):
    if email_hash.endswith('.jpg'):
        email_hash = email_hash[:-4]
    try:
        size = int(request.GET.get('s', DEFAULT_WIDTH))
    except ValueError:
        size = DEFAULT_WIDTH
    if size > MAX_WIDTH:
        size = MAX_WIDTH
    rating = request.GET.get('r', 'g') # Unused, for now.
    default = request.GET.get('d', '')
    data = None
    try:
        avatar = Avatar.objects.filter(email_hash=email_hash).order_by('-primary', '-date_uploaded')[0]
    except IndexError:
        avatar = None
    except Avatar.MultipleObjectsReturned:
        avatar = None
    try:
        if avatar is not None:
            data = open(avatar.avatar.path, 'r').read()
    except IOError:
        pass
    if not data and default:
        try:
            data = urlopen(default).read()
        except: #TODO: Fix this hardcore
            pass
    if not data:
        filename = os.path.join(os.path.dirname(__file__), 'default.jpg')
        data = open(filename, 'r').read()
    p = ImageFile.Parser()
    p.feed(data)
    try:
        image = p.close()
    except IOError:
        filename = os.path.join(os.path.dirname(__file__), 'default.jpg')
        try:
            return HttpResponse(open(filename, 'r').read(), mimetype='image/jpeg')
        except: #TODO: Fix this hardcore
            # Is this the right response after so many other things have failed?
            raise Http404
    (width, height) = image.size
    if width > height:
        diff = (width - height) / 2
        image = image.crop((diff, 0, width - diff, height))
    else:
        diff = (height - width) / 2
        image = image.crop((0, diff, width, height - diff))
    image = image.resize((size, size), AVATAR_RESIZE_METHOD)
    response = HttpResponse(mimetype='image/jpeg')
    image.save(response, "JPEG")
    return response

def change(request, extra_context={}, next_override=None):
    avatars = Avatar.objects.filter(user=request.user).order_by('-primary')
    if avatars.count() > 0:
        avatar = avatars[0]
        kwargs = {'initial': {'choice': avatar.id}}
    else:
        avatar = None
        kwargs = {}
    primary_avatar_form = PrimaryAvatarForm(request.POST or None, user=request.user, **kwargs)
    if request.method == "POST":
        if 'avatar' in request.FILES:
            path = avatar_file_path(user=request.user, 
                filename=request.FILES['avatar'].name)
            try:
                os.makedirs(os.path.join(
                    settings.MEDIA_ROOT, "/".join(path.split('/')[:-1])))
            except OSError, e:
                pass # The dirs already exist.
            new_file = default_storage.open(path, 'wb')
            for i, chunk in enumerate(request.FILES['avatar'].chunks()):
                if i * 16 == MAX_MEGABYTES:
                    raise Http404 # TODO: Is this the right thing to do?
                                  # Validation error maybe, instead?
                new_file.write(chunk)
            avatar = Avatar(
                user = request.user,
                primary = True,
                avatar = path,
            )
            avatar.save()
            new_file.close()
            request.user.message_set.create(
                message=_("Successfully uploaded a new avatar."))
        if 'choice' in request.POST and primary_avatar_form.is_valid():
            avatar = Avatar.objects.get(id=
                primary_avatar_form.cleaned_data['choice'])
            avatar.primary = True
            avatar.save()
            request.user.message_set.create(
                message=_("Successfully updated your avatar."))
        return HttpResponseRedirect(next_override or _get_next(request))
    return render_to_response(
        'avatar/change.html',
        extra_context,
        context_instance = RequestContext(
            request,
            { 'avatar': avatar, 
              'avatars': avatars,
              'primary_avatar_form': primary_avatar_form,
              'next': next_override or _get_next(request), }
        )
    )
change = login_required(change)

def delete(request, extra_context={}, next_override=None):
    avatars = Avatar.objects.filter(user=request.user).order_by('-primary')
    if avatars.count() > 0:
        avatar = avatars[0]
    else:
        avatar = None
    delete_avatar_form = DeleteAvatarForm(request.POST or None, user=request.user)
    if request.method == 'POST':
        if delete_avatar_form.is_valid():
            ids = delete_avatar_form.cleaned_data['choices']
            Avatar.objects.filter(id__in=ids).delete()
            request.user.message_set.create(
                message=_("Successfully deleted the requested avatars."))
            return HttpResponseRedirect(next_override or _get_next(request))
    return render_to_response(
        'avatar/confirm_delete.html',
        extra_context,
        context_instance = RequestContext(
            request,
            { 'avatar': avatar, 
              'avatars': avatars,
              'delete_avatar_form': delete_avatar_form,
              'next': next_override or _get_next(request), }
        )
    )
change = login_required(change)
