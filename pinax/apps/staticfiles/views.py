"""
Views and functions for serving static files. These are only to be used
during development, and SHOULD NOT be used in a production setting.
"""

import mimetypes
import os
import posixpath
import stat
import urllib

from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseNotModified
from django.utils.http import http_date
from django.views.static import was_modified_since, directory_index
from django.conf import settings

SITE_MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT',
    os.path.join(settings.PROJECT_ROOT, 'site_media'))
PINAX_MEDIA_ROOT = os.path.join(settings.PINAX_ROOT, 'media', settings.PINAX_THEME)
PROJECT_MEDIA_ROOT = os.path.join(settings.PROJECT_ROOT, 'media')
PINAX_APP_MEDIA_DIRS = ('media', 'static', 'site_media')

def get_media_path(path):
    """
    Traverses the following locations to find a requested media file in the
    given order and return the absolute file path:

    1. The site media path, e.g. for user-contributed files:
        <project>/site_media/<path>
    2. Current project:
        <project>/media/<app>/<path>
    3. Pinax' themes:
        pinax/media/<theme>/<path>
    4. Installed apps:
        a) <app>/media|static|site_media/<app>/<path>
        b) <app>/media|static|site_media/<path>
    """
    app_labels = settings.INSTALLED_APPS
    short_app_labels = [label.split('.')[-1] for label in app_labels]
    for location in (SITE_MEDIA_ROOT, PROJECT_MEDIA_ROOT, PINAX_MEDIA_ROOT):
        media = os.path.join(location, path)
        if os.path.exists(media):
            return media
    for app in settings.INSTALLED_APPS:
        app = __import__(app, {}, {}, [''])
        app_root = os.path.dirname(app.__file__)
        for media_dir in PINAX_APP_MEDIA_DIRS:
            media = os.path.join(app_root, media_dir, path)
            if os.path.exists(media):
                return media
            splitted_path = path.split('/', 1)
            if len(splitted_path) > 1:
                app, newpath = splitted_path
                if app in short_app_labels:
                    media = os.path.join(app_root, media_dir, newpath)
                    if os.path.exists(media):
                        return media
    return None

def serve(request, path, show_indexes=False):
    """
    Serve static files below a given point in the directory structure.

    To use, put a URL pattern such as::

        (r'^(?P<path>.*)$', 'staticfiles.views.serve')

    in your URLconf. You may also set ``show_indexes`` to ``True`` if you'd
    like to serve a basic index of the directory.  This index view will use
    the template hardcoded below, but if you'd like to override it, you
    can create a template called ``static/directory_index``.
    """

    # Clean up given path to only allow serving files below document_root.
    path = posixpath.normpath(urllib.unquote(path))
    path = path.lstrip('/')
    newpath = ''
    for part in path.split('/'):
        if not part:
            # Strip empty path components.
            continue
        drive, part = os.path.splitdrive(part)
        head, part = os.path.split(part)
        if part in (os.curdir, os.pardir):
            # Strip '.' and '..' in path.
            continue
        newpath = os.path.join(newpath, part).replace('\\', '/')
    if newpath and path != newpath:
        return HttpResponseRedirect(newpath)
    fullpath = get_media_path(newpath)
    if fullpath is None:
        raise Http404, '"%s" does not exist' % newpath
    if not os.path.exists(fullpath):
        raise Http404, '"%s" does not exist' % fullpath
    if os.path.isdir(fullpath):
        if show_indexes:
            return directory_index(newpath, fullpath)
        raise Http404, "Directory indexes are not allowed here."
    # Respect the If-Modified-Since header.
    statobj = os.stat(fullpath)
    if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                              statobj[stat.ST_MTIME], statobj[stat.ST_SIZE]):
        return HttpResponseNotModified()
    mimetype = mimetypes.guess_type(fullpath)[0] or 'application/octet-stream'
    contents = open(fullpath, 'rb').read()
    response = HttpResponse(contents, mimetype=mimetype)
    response["Last-Modified"] = http_date(statobj[stat.ST_MTIME])
    response["Content-Length"] = len(contents)
    return response

