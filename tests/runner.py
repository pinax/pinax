import os
import sys

from django.conf import settings
from django.core.management import setup_environ, call_command

import pinax
from pinax.utils.importlib import import_module


PINAX_ROOT = os.path.abspath(os.path.dirname(pinax.__file__))


PROJECT_APP_DIRS = []


# setup sys.path for Pinax and projects
sys.path.insert(0, os.path.join(PINAX_ROOT, "apps"))
sys.path.insert(0, os.path.join(PINAX_ROOT, "projects"))


def setup_project(name):
    sys.path.insert(0, os.path.join(PINAX_ROOT, "projects", name))
    project_app_dir = os.path.join(PINAX_ROOT, "projects", name, "apps")
    PROJECT_APP_DIRS.append(project_app_dir)
    sys.path.insert(0, project_app_dir)
    settings_mod = import_module("%s.settings" % name)
    setup_environ(settings_mod)


def reset_project():
    del sys.path[:2]


#
# thoughts on a test runner. the goal is to run all tests in Pinax.
# tests live in apps. one approach is to run each project tests. however,
# this will result in potentionally running tests more than once for an
# app. rather, we can setup a fake project for each app and then run
# their tests.
#


def main():
    projects = [
        "basic_project",
        "code_project",
        "intranet_project",
        "private_beta_project",
        "sample_group_project",
        "social_project",
    ]
    
    installed_apps = set()
    
    for project in projects:
        setup_project(project)
        settings._setup()
        installed_apps.update(set(settings.INSTALLED_APPS))
        reset_project()
    
    # @@@ remove some apps that we need to deal with later
    #installed_apps.remove("django_openid")
    
    # setup path for all project apps/
    sys.path = PROJECT_APP_DIRS + sys.path[:]
    
    # reset settings
    settings._wrapped = None
    
    # set up settings for running tests for all apps
    settings.configure(**{
        "DATABASE_ENGINE": "sqlite3",
        "SITE_ID": 1,
        "ROOT_URLCONF": "",
        "MIDDLEWARE_CLASSES": [
            "django.middleware.common.CommonMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
        ],
        "INSTALLED_APPS": list(installed_apps),
    })
    
    call_command("test")


if __name__ == "__main__":
    main()
