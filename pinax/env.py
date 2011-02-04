import os
import sys

from django.utils.importlib import import_module


def setup_environ(dunder_file=None, project_path=None):
    assert not (dunder_file and project_path), ("You must not specify both "
        "__file__ and project_path")
    
    if dunder_file is not None:
        file_path = os.path.abspath(os.path.dirname(dunder_file))
        deploy_files = [
            "fcgi.py", "fcgi.pyc",
            "wsgi.py", "wsgi.pyc",
        ]
        if os.path.basename(dunder_file) in deploy_files:
            project_path = os.path.abspath(os.path.join(file_path, os.pardir))
        else:
            project_path = file_path
            
    # the basename must be the project name and importable.
    project_name = os.path.basename(project_path)
    
    # setup Django correctly (the hard-coding of settings is only temporary.
    # carljm's proposal will remove that)
    os.environ["DJANGO_SETTINGS_MODULE"] = "%s.settings" % project_name
    
    # ensure the importablity of project
    sys.path.append(os.path.join(project_path, os.pardir))
    import_module(project_name)
    sys.path.pop()
    
    # Pinax adds an app directory for users as a reliable location for
    # Django apps
    sys.path.insert(0, os.path.join(project_path, "apps"))
