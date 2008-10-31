
import os
import sys

from os.path import abspath, dirname, join
from site import addsitedir

from django.core.handlers.modpython import ModPythonHandler

class PinaxModPythonHandler(ModPythonHandler):
    def __call__(self, req):
        # mod_python fakes the environ, and thus doesn't process SetEnv. 
        # This fixes that. Django will call this again since there is no way
        # of overriding __call__ to just process the request.
        os.environ.update(req.subprocess_env)
        from django.conf import settings
        
        sys.path.insert(0, abspath(join(dirname(__file__), "../../")))
        
        path = addsitedir(join(settings.PINAX_ROOT, "libs/external_libs"), set())
        if path:
            sys.path = list(path) + sys.path
            
        sys.path.insert(0, join(settings.PINAX_ROOT, "apps/external_apps"))
        sys.path.insert(0, join(settings.PINAX_ROOT, "apps/local_apps"))
        sys.path.insert(0, join(settings.PROJECT_ROOT, "apps"))
        
        return super(PinaxModPythonHandler, self).__call__(req)

def handler(req):
    # mod_python hooks into this function.
    return PinaxModPythonHandler()(req)
