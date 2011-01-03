import optparse
import os
import sys

from django.conf import settings
from django.core.management import setup_environ, call_command

import pinax
import pinax.env

#
# thoughts on a test runner. the goal is to run all tests in Pinax.
# tests live in apps. one approach is to run each project tests. however,
# this will result in potentionally running tests more than once for an
# app. rather, we can setup a fake project for each app and then run
# their tests.
#


PINAX_ROOT = os.path.abspath(os.path.dirname(pinax.__file__))
PINAX_PROJECTS = [
    "zero_project",
    "account_project",
    "basic_project",
    "static_project",
    "code_project",
    "company_project",
    "intranet_project",
    "private_beta_project",
    "sample_group_project",
    "social_project",
]
EXTRA_APP_ALIASES = {
    "django_filters": ["django_filters.tests"],
}


def setup_project(name):
    """
    Helper for build_app_list to prepare the process for settings of a given
    Pinax project.
    """
    project_path = os.path.join(PINAX_ROOT, "projects", name)
    pinax.env.setup_environ(project_path=project_path)


def build_app_list(projects):
    """
    Given a list of projects return a unique list of apps.
    """
    apps = set()
    
    for project in projects:
        setup_project(project)
        settings._setup()
        for app in settings.INSTALLED_APPS:
            if app in EXTRA_APP_ALIASES:
                apps.update(EXTRA_APP_ALIASES[app])
            apps.add(app)
    
    return list(apps)


def build_project_app_paths(projects):
    app_dirs = []
    for project in projects:
        app_dir = os.path.join(PINAX_ROOT, "projects", project, "apps")
        app_dirs.append(app_dir)
    return app_dirs


def setup_test_environment():
    apps = build_app_list(PINAX_PROJECTS)
    
    # setup path for all project apps/
    sys.path = build_project_app_paths(PINAX_PROJECTS) + sys.path[:]
    
    # reset settings
    settings._wrapped = None
    
    # set up settings for running tests for all apps
    settings.configure(**{
        "DATABASE_ENGINE": "sqlite3",
        "SITE_ID": 1,
        "ROOT_URLCONF": "",
        "STATIC_URL": "/site_media/static/",
        "MIDDLEWARE_CLASSES": [
            "django.middleware.common.CommonMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ],
        "INSTALLED_APPS": apps,
        "LOGIN_URL": "/account/login/",
        
        "TEMPLATE_DIRS": [
            os.path.join(os.path.dirname(__file__), "templates"),
            os.path.join(os.path.dirname(pinax.__file__), "templates", "default"),
        ],
        
        # these settings are currently required to support Pinax default
        # templates.
        "TEMPLATE_CONTEXT_PROCESSORS": [
            "django.contrib.auth.context_processors.auth",
            "django.core.context_processors.debug",
            "django.core.context_processors.i18n",
            "django.core.context_processors.media",
            "django.core.context_processors.request",
            "django.contrib.messages.context_processors.messages",
            "pinax.core.context_processors.pinax_settings",
        ],
        "CONTACT_EMAIL": "feedback@example.com",
        "SITE_NAME": "Pinax",
    })


def main():
    
    usage = "%prog [options] [app app app]"
    parser = optparse.OptionParser(usage=usage)
    
    parser.add_option("-v", "--verbosity",
        action = "store",
        dest = "verbosity",
        default = "0",
        type = "choice",
        choices = ["0", "1", "2"],
        help = "verbosity level; 0=minimal output, 1=normal output, 2=all output",
    )
    parser.add_option("--coverage",
        action = "store_true",
        dest = "coverage",
        default = False,
        help = "hook in coverage during test suite run and save out results",
    )
    
    options, args = parser.parse_args()
    
    if options.coverage:
        try:
            import coverage
        except ImportError:
            sys.stderr.write("coverage is not installed.\n")
            sys.exit(1)
        else:
            cov = coverage.coverage(auto_data=True)
            cov.start()
    else:
        cov = None
    
    setup_test_environment()
    
    call_command("test", verbosity=int(options.verbosity), *args)
    
    if cov:
        cov.stop()
        cov.save()


if __name__ == "__main__":
    main()
