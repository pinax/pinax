#!/usr/bin/env python

import sys
import os
import glob
from os.path import abspath, dirname, join
from site import addsitedir

# For right now this script assumes you're in the pinax/fixtures/generate dir.
path = addsitedir(abspath(join(dirname(__file__), '../../../site-packages')), set())
if path: sys.path = list(path) + sys.path
sys.path.insert(0, abspath(join(dirname(__file__), '../../../apps')))
sys.path.insert(0, abspath(join(dirname(__file__), '../../local_apps')))

sys.path.append('../../../')
os.environ['DJANGO_SETTINGS_MODULE'] = 'pinax.settings'

from django.conf import settings
settings.DATABASE_ENGINE = 'sqlite3'
settings.DATABASE_NAME = ':memory:'

from django.core.management.commands.dumpdata import Command as DumpdataCommand
from django.core.management.commands.syncdb import Command as SyncDBCommand

FIXTURES_TO_GENERATE = ('auth', 'profiles', 'friends', 'microblogging')

def main():
    SyncDBCommand().handle_noargs(interactive=False)
    for module_name in FIXTURES_TO_GENERATE:
        full_module_name = 'pinax.fixtures.generate.%s' % (module_name,)
        mod = __import__(full_module_name)
        for comp in full_module_name.split('.')[1:]:
            mod = getattr(mod, comp)
        mod.generate()
        path = abspath('../%s.json' % module_name)
        fixture_file = open(path, 'w')
        fixture_file.write(DumpdataCommand().handle(module_name))
        fixture_file.close()
        print "Fixture written to %s" % path

if __name__ == "__main__":
    main()