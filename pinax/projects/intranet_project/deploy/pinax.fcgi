# pinax.fcgi is configured to live in projects/intranet_project/deploy.

import os
import sys

from os.path import abspath, dirname, join
from site import addsitedir

sys.path.insert(0, abspath(join(dirname(__file__), "../../")))

from django.conf import settings
os.environ["DJANGO_SETTINGS_MODULE"] = "intranet_project.settings"

sys.path.insert(0, join(settings.PINAX_ROOT, "apps"))
sys.path.insert(0, join(settings.PROJECT_ROOT, "apps"))

from django.core.servers.fastcgi import runfastcgi
runfastcgi(method="threaded", daemonize="false")
