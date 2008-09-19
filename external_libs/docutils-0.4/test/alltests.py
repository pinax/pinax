#!/bin/sh
''''exec python -u "$0" "$@" #'''

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 4217 $
# Date: $Date: 2005-12-15 04:09:04 +0100 (Thu, 15 Dec 2005) $
# Copyright: This module has been placed in the public domain.

__doc__ = \
"""
All modules named 'test_*.py' in the current directory, and recursively in
subdirectories (packages) called 'test_*', are loaded and test suites within
are run.
"""

import time
# Start point for actual elapsed time, including imports
# and setup outside of unittest.
start = time.time()

import sys
import os
from types import UnicodeType
import DocutilsTestSupport              # must be imported before docutils
import docutils


def new_exception_str(self):
    for i in self.args:
        if isinstance(i, UnicodeType):
            raise RuntimeError('Error (unicode): %r' % (self.args,))
    return old_exception_str(self)

old_exception_str = Exception.__str__
Exception.__str__ = new_exception_str


class Tee:

    """Write to a file and a stream (default: stdout) simultaneously."""

    def __init__(self, filename, stream=sys.__stdout__):
        self.file = open(filename, 'w')
        self.stream = stream

    def write(self, string):
        self.stream.write(string)
        self.file.write(string)

    def flush(self):
        self.stream.flush()
        self.file.flush()


def pformat(suite):
    step = 4
    suitestr = repr(suite).replace('=[<', '=[\n<').replace(', ', ',\n')
    indent = 0
    output = []
    for line in suitestr.splitlines():
        output.append(' ' * indent + line)
        if line[-1:] == '[':
            indent += step
        else:
            if line [-5:] == ']>]>,':
                indent -= step * 2
            elif line[-3:] == ']>,':
                indent -= step
    return '\n'.join(output)

def suite():
    path, script = os.path.split(sys.argv[0])
    suite = package_unittest.loadTestModules(DocutilsTestSupport.testroot,
                                             'test_', packages=1)
    sys.stdout.flush()
    return suite

# must redirect stderr *before* first import of unittest
sys.stdout = sys.stderr = Tee('alltests.out')

import package_unittest


if __name__ == '__main__':
    suite = suite()
    print ('Testing Docutils %s [%s] with Python %s on %s at %s'
           % (docutils.__version__, docutils.__version_details__,
              sys.version.split()[0],
              time.strftime('%Y-%m-%d'), time.strftime('%H:%M:%S')))
    print 'Working directory: %s' % os.getcwd()
    print 'Docutils package: %s' % os.path.dirname(docutils.__file__)
    sys.stdout.flush()
    package_unittest.main(suite)
    #if package_unittest.verbosity > 1:
    #    print >>sys.stderr, pformat(suite) # check the test suite
    finish = time.time()
    print 'Elapsed time: %.3f seconds' % (finish - start)
