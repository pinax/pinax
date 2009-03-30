#!/usr/bin/env python

import sys

from os.path import abspath, join
from site import addsitedir

sys.path.insert(0, abspath('../projects/social_project'))

from django.conf import settings
from django.core.management import setup_environ, call_command

try:
    import settings as settings_mod # Assumed to be in the same directory.
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

# setup the environment before we start accessing things in the settings.
setup_environ(settings_mod)

path = addsitedir(join(settings.PINAX_ROOT, "libs/external_libs"), set())
if path:
    sys.path = list(path) + sys.path
sys.path.insert(0, join(settings.PINAX_ROOT, "apps"))
sys.path.insert(0, join(settings.PROJECT_ROOT, "apps"))

settings.DATABASE_ENGINE = 'sqlite3'
settings.DATABASE_NAME = ':memory:'
settings.NOTIFICATION_QUEUE_ALL = True

from django.core.management.commands.dumpdata import Command as DumpdataCommand

# These are in a specific order.  Please make sure to know what you are doing
# before rearranging them.
POSSIBLE_FIXTURES = (
    'auth',
    'notification',
    'profiles',
    'account',
    'friends',
    'microblogging',
    'announcements',
)

POST_GEN_MODULES = (
    'send_notifications',
)

def main():
    fixtures = sys.argv[1:]
    if fixtures:
        for fixture in fixtures:
            if fixture not in POSSIBLE_FIXTURES:
                print "%s not a possible fixture to generate." % (fixture,)
                print "The possibilities are: %s" % (', '.join(
                    POSSIBLE_FIXTURES),)
                sys.exit(1)
    else:
        fixtures = POSSIBLE_FIXTURES
    print "Generating fixtures for %s" % (', '.join(fixtures),)
    call_command('syncdb')
    for module_name in fixtures:
        full_module_name = 'generate.gen_%s' % (module_name,)
        mod = __import__(full_module_name)
        for comp in full_module_name.split('.')[1:]:
            mod = getattr(mod, comp)
        mod.generate()
    for module_name in POST_GEN_MODULES:
        full_module_name = 'generate.%s' % (module_name,)
        mod = __import__(full_module_name)
        for comp in full_module_name.split('.')[1:]:
            mod = getattr(mod, comp)
        mod.generate()
    for module_name in fixtures:
        path = abspath('%s.json' % module_name)
        fixture_file = open(path, 'w')
        fixture_file.write(DumpdataCommand().handle(module_name))
        fixture_file.close()
        print "Fixture written to %s" % path

if __name__ == "__main__":
    main()