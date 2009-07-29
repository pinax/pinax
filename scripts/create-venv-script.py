#!/usr/bin/env python
"""
Call this like ``python pinax/bin/create-venv-script.py``
it will refresh the pinax-boot.py script
"""
import os
import virtualenv
from optparse import OptionParser
from os.path import join, exists, dirname, abspath

def main():
    usage = "usage: %prog [options]"
    description = "Creates a Pinax boot script and uses version specific installer templates if given a release version."
    parser = OptionParser(usage, description=description)
    parser.add_option("-r", "--release",
                      metavar='VERSION', dest='release', default=None,
                      help='Release version of Pinax to bootstrap')
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose")
    (options, args) = parser.parse_args()

    here = dirname(abspath(__file__))

    script_name = join(here, 'pinax-boot.py')
    installer = join(here, '_installer.py') # _installer.py

    if options.release:
        release_installer = join(here, 'installers', '%s.py' % options.release) # installers/<version>.py
        if exists(release_installer):
            installer = release_installer
            script_name = join(here, 'pinax-boot-%s.py' % options.release) # pinax-boot-<version>.py

    print "Using as template: %s" % installer

    extra_text = open(installer).read()
    text = virtualenv.create_bootstrap_script(extra_text)
    if os.path.exists(script_name):
        f = open(script_name)
        cur_text = f.read()
        f.close()
    else:
        cur_text = ''

    print 'Updating %s' % script_name

    if cur_text == text:
        print 'No update'
    else:
        if options.verbose:
            print 'Script changed; updating...'
        f = open(script_name, 'w')
        f.write(text)
        f.close()

if __name__ == '__main__':
    main()
