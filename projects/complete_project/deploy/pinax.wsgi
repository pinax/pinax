# pinax.wsgi is configured to live in projects/complete_project/deploy. If you
# move this file you need to reconfigure the paths below.

import os
import sys

# redirect sys.stdout to sys.stderr for bad libraries like geopy that uses
# print statements for optional import exceptions.
sys.stdout = sys.stderr

from os.path import abspath, dirname, join
from site import addsitedir

path = addsitedir(abspath(join(dirname(__file__), "../../../libs/external_libs")), set())
if path:
    sys.path = list(path) + sys.path

sys.path.insert(0, abspath(join(dirname(__file__), "../../../apps/external_apps")))
sys.path.insert(0, abspath(join(dirname(__file__), "../../../apps/local_apps")))
sys.path.insert(0, abspath(join(dirname(__file__), "../../../apps/core_apps")))

# emulate manage.py path hacking.
sys.path.insert(0, abspath(join(dirname(__file__), "../../")))
sys.path.insert(0, abspath(join(dirname(__file__), "../")))

from django.core.handlers.wsgi import WSGIHandler

os.environ["DJANGO_SETTINGS_MODULE"] = "complete_project.settings"

application = WSGIHandler()
