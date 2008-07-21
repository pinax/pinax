#!/usr/bin/env python
from os.path import abspath, dirname, join
from site import addsitedir
import sys
path = addsitedir(abspath(join(dirname(__file__), 'site-packages')), set())
if path: sys.path = list(path) + sys.path

from django.core.management import execute_manager
try:
    import settings # Assumed to be in the same directory.
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)
