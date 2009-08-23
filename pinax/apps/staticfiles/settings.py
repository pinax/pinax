import os.path
from django.conf import settings

ROOT = getattr(settings,
    'STATIC_ROOT',
    os.path.join(settings.PROJECT_ROOT, 'site_media', 'static'))
DIRS = getattr(settings,
    'STATIC_DIRS', ())
MEDIA_DIRNAMES = getattr(settings,
    'STATIC_MEDIA_DIRNAMES', ['media'])
PREPEND_LABEL_APPS = getattr(settings,
    'STATIC_PREPEND_LABEL_APPS', ('django.contrib.admin',))
