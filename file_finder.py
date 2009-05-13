#!/usr/bin/env python

"""
A hook into setuptools for files not under VCS.

based on setuptools_git and ella's setuptools_entry.py
"""

import re
import os
from os.path import join

# do not include /build/ dir, *.egg-info dir and py[co] files
EXCLUDE = re.compile(r'(^build|^\.hg|^\.DS_Store|^\.git|[^/]+\.egg-info|.*.py[co]$)')

def walk(top):
    files = []

    def _walk(top, dir):
        try:
            names = os.listdir(top)
        except os.error:
            return

        for name in names:
            _name = join(dir, name)
            _top = join(top, name)
            if os.path.isdir(_top):
                _walk(_top, _name)
            else:
                files.append(_name)

    _walk(top, '')
    return files

def dummylsfiles(dirname=""):
    if not dirname:
        dirname = '.'

    try:
        files = walk(dirname)
    except:
        # Something went terribly wrong but the setuptools doc says we
        # must be strong in the face of danger.  We shall not run away
        # in panic.
        return []

    return [f for f in files if not EXCLUDE.match(f)]

if __name__ == "__main__":
    import sys
    from pprint import pprint

    if len(sys.argv) != 2:
        print "USAGE: %s DIRNAME" % sys.argv[0]
        sys.exit(1)

    pprint(dummylsfiles(sys.argv[1]))

