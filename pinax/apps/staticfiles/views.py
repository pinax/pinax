"""
Views and functions for serving static files. These are only to be used
during development, and SHOULD NOT be used in a production setting.
"""

import os
import stat
import urllib
import mimetypes
import posixpath

from django.utils.http import http_date
from django.views.static import was_modified_since, directory_index
from django.http import Http404, HttpResponse, HttpResponseRedirect, \
    HttpResponseNotModified
from staticfiles.utils import get_media_path

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
    mimetype = mimetypes.guess_type(fullpath)[0] or 'application/octet-stream'
    if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                              statobj[stat.ST_MTIME], statobj[stat.ST_SIZE]):
        return HttpResponseNotModified(mimetype=mimetype)
    contents = open(fullpath, 'rb').read()
    response = HttpResponse(contents, mimetype=mimetype)
    response["Last-Modified"] = http_date(statobj[stat.ST_MTIME])
    response["Content-Length"] = len(contents)
    return response
