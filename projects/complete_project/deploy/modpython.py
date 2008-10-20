
import os
import sys

from os.path import abspath, dirname, join
from site import addsitedir

from django.core.handlers.modpython import ModPythonHandler

PINAX_ROOT = abspath(join(dirname(__file__), "../../../"))
PROJECT_ROOT = abspath(join(dirname(__file__), "../"))

class PinaxModPythonHandler(ModPythonHandler):
    def __call__(self, req):
        path = addsitedir(join(PINAX_ROOT, "libs/external_libs"), set())
        if path:
            sys.path = list(path) + sys.path
            
        sys.path.insert(0, join(PINAX_ROOT, "apps/external_apps"))
        sys.path.insert(0, join(PINAX_ROOT, "apps/local_apps"))
        sys.path.insert(0, join(PROJECT_ROOT, "apps"))
        
        sys.path.insert(0, abspath(join(dirname(__file__), "../../")))
        
        return super(PinaxModPythonHandler, self).__call__(req)

def handler(req):
    # mod_python hooks into this function.
    return PinaxModPythonHandler()(req)
