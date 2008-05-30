#!/usr/bin/env python

import sys
sys.path.insert(0, 'lib/python-openid-2.1.1')
sys.path.insert(0, 'lib/python-yadis-1.1.0')
sys.path.insert(0, 'lib/docutils-0.4')
sys.path.insert(0, 'lib/textile-2.0.11')
sys.path.insert(0, 'lib/markdown-1.7')
sys.path.insert(0, 'lib/pytz-2008b')

from django.core.management import execute_manager
try:
    import settings # Assumed to be in the same directory.
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)
