#!/usr/bin/env python
import sys

from os.path import abspath, dirname, join
from site import addsitedir

PINAX_ROOT = abspath(join(dirname(__file__), "../../"))
PROJECT_ROOT = abspath(dirname(__file__))

path = addsitedir(join(PINAX_ROOT, "libs/external_libs"), set())
if path:
    sys.path = list(path) + sys.path
sys.path.insert(0, join(PINAX_ROOT, "apps/external_apps"))
sys.path.insert(0, join(PINAX_ROOT, "apps/local_apps"))
sys.path.insert(0, join(PROJECT_ROOT, "apps"))

from django.core.management import execute_manager

try:
    import settings # Assumed to be in the same directory.
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)
