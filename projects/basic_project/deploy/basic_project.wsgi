# basic_project.wsgi is configured to live in projects/basic_project/deploy.
# If you move this file you need to reconfigure the paths below.

import os
import sys

# redirect sys.stdout to sys.stderr for bad libraries like geopy that uses
# print statements for optional import exceptions.
sys.stdout = sys.stderr

from os.path import abspath, dirname, join
from site import addsitedir

PINAX_ROOT = abspath(join(dirname(__file__), "../../../"))
PROJECT_ROOT = abspath(join(dirname(__file__), "../"))

path = addsitedir(join(PINAX_ROOT, "libs/external_libs"), set())
if path:
    sys.path = list(path) + sys.path

sys.path.insert(0, join(PINAX_ROOT, "apps/external_apps"))
sys.path.insert(0, join(PINAX_ROOT, "apps/local_apps"))
sys.path.insert(0, join(PROJECT_ROOT, "apps"))

sys.path.insert(0, abspath(join(dirname(__file__), "../../")))

from django.core.handlers.wsgi import WSGIHandler

os.environ["DJANGO_SETTINGS_MODULE"] = "basic_project.settings"

application = WSGIHandler()
