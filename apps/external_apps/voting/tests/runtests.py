import os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'voting.tests.settings'

from django.test.simple import run_tests

failures = run_tests(None, verbosity=9)
if failures:
    sys.exit(failures)
