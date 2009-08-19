import os
import sys
from django.conf import settings

SITE_MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT',
    os.path.join(settings.PROJECT_ROOT, 'site_media'))
EXTRA_MEDIA = getattr(settings, 'STATICFILES_EXTRA_MEDIA', ())
MEDIA_DIRNAMES = getattr(settings, 'STATICFILES_MEDIA_DIRNAMES', ['media'])

def get_media_path(path, all=False):
    """
    Traverses the following locations to find a requested media file in the
    given order and return the absolute file path:

    1. The site media path, e.g. for user-contributed files, e.g.:
        <project>/site_media/<path>
    2. Any extra media locations given in the settings
    4. Installed apps:
        a) <app>/media/<app>/<path>
        b) <app>/media/<path>
    """
    collection = []
    for location in [SITE_MEDIA_ROOT] + [root for label, root in EXTRA_MEDIA]:
        media = os.path.join(location, path)
        if os.path.exists(media):
            if not all:
                return media
            collection.append(media)

    installed_apps = settings.INSTALLED_APPS
    app_labels = [label.split('.')[-1] for label in installed_apps]
    for app in installed_apps:
        app_mod = import_module(app)
        app_root = os.path.dirname(app_mod.__file__)
        for media_dir in MEDIA_DIRNAMES:
            media = os.path.join(app_root, media_dir, path)
            if os.path.exists(media):
                if not all:
                    return media
                collection.append(media)
            splitted_path = path.split('/', 1)
            if len(splitted_path) > 1:
                app_name, newpath = splitted_path
                if app_name in app_labels:
                    media = os.path.join(app_root, media_dir, newpath)
                    if os.path.exists(media):
                        if not all:
                            return media
                        collection.append(media)
    return collection or None

def _resolve_name(name, package, level):
    """Return the absolute name of the module to be imported."""
    if not hasattr(package, 'rindex'):
        raise ValueError("'package' not set to a string")
    dot = len(package)
    for x in xrange(level, 1, -1):
        try:
            dot = package.rindex('.', 0, dot)
        except ValueError:
            raise ValueError("attempted relative import beyond top-level "
                              "package")
    return "%s.%s" % (package[:dot], name)

def import_module(name, package=None):
    """Import a module.

    The 'package' argument is required when performing a relative import. It
    specifies the package to use as the anchor point from which to resolve the
    relative import to an absolute import.

    """
    if name.startswith('.'):
        if not package:
            raise TypeError("relative imports require the 'package' argument")
        level = 0
        for character in name:
            if character != '.':
                break
            level += 1
        name = _resolve_name(name[level:], package, level)
    __import__(name)
    return sys.modules[name]
