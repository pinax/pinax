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
    installer_template = join(here, 'installers', 'dev.py')
    script_name = join(here, 'pinax-boot.py')

    if options.release:
        installer_template = join(here, 'installers', '%s.py' % options.release) # installers/0.7b1.py
        if not exists(installer_template):
            parser.error("template for release %s could not be found" % options.release)
        script_name = join(here, 'pinax-boot-%s.py' % options.release) # pinax-boot-0.7b1.py

    if options.verbose:
        print "Using as template: %s" % installer_template

    extra_text = open(installer_template).read()
    text = virtualenv.create_bootstrap_script(extra_text)
    if os.path.exists(script_name):
        f = open(script_name)
        cur_text = f.read()
        f.close()
    else:
        cur_text = ''

    if options.verbose:
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
