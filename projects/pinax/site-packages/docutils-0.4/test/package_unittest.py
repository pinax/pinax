#! /usr/bin/env python

# Author: Garth Kidd
# Contact: garth@deadlybloodyserious.com
# Revision: $Revision: 2454 $
# Date: $Date: 2004-07-25 13:29:43 +0200 (Sun, 25 Jul 2004) $
# Copyright: This module has been placed in the public domain.

"""
This module extends unittest.py with `loadTestModules()`, by loading multiple
test modules from a directory.  Optionally, test packages are also loaded,
recursively.
"""

import sys
import os
import getopt
import types
import unittest
import re


# So that individual test modules can share a bit of state,
# `package_unittest` acts as an intermediary for the following
# variables:
debug = 0
verbosity = 1

USAGE = """\
Usage: test_whatever [options]

Options:
  -h, --help       Show this message
  -v, --verbose    Verbose output
  -q, --quiet      Minimal output
  -d, --debug      Debug mode
"""

def usageExit(msg=None):
    """Print usage and exit."""
    if msg:
        print msg
    print USAGE
    sys.exit(2)

def parseArgs(argv=sys.argv):
    """Parse command line arguments and set TestFramework state.

    State is to be acquired by test_* modules by a grotty hack:
    ``from TestFramework import *``. For this stylistic
    transgression, I expect to be first up against the wall
    when the revolution comes. --Garth"""
    global verbosity, debug
    try:
        options, args = getopt.getopt(argv[1:], 'hHvqd',
                                      ['help', 'verbose', 'quiet', 'debug'])
        for opt, value in options:
            if opt in ('-h', '-H', '--help'):
                usageExit()
            if opt in ('-q', '--quiet'):
                verbosity = 0
            if opt in ('-v', '--verbose'):
                verbosity = 2
            if opt in ('-d', '--debug'):
                debug =1
        if len(args) != 0:
            usageExit("No command-line arguments supported yet.")
    except getopt.error, msg:
        usageExit(msg)

def loadTestModules(path, name='', packages=None):
    """
    Return a test suite composed of all the tests from modules in a directory.

    Search for modules in directory `path`, beginning with `name`. If
    `packages` is true, search subdirectories (also beginning with `name`)
    recursively.  Subdirectories must be Python packages; they must contain an
    '__init__.py' module.
    """
    testLoader = unittest.defaultTestLoader
    testSuite = unittest.TestSuite()
    testModules = []
    path = os.path.abspath(path)        # current working dir if `path` empty
    paths = [path]
    while paths:
        p = paths.pop(0)
        files = os.listdir(p)
        for filename in files:
            if filename.startswith(name):
                fullpath = os.path.join(p, filename)
                if filename.endswith('.py'):
                    fullpath = fullpath[len(path)+1:]
                    testModules.append(path2mod(fullpath))
                elif packages and os.path.isdir(fullpath) and \
                      os.path.isfile(os.path.join(fullpath, '__init__.py')):
                    paths.append(fullpath)
    # Import modules and add their tests to the suite.
    sys.path.insert(0, path)
    for mod in testModules:
        if debug:
            print >>sys.stderr, "importing %s" % mod
        try:
            module = import_module(mod)
        except ImportError:
            print >>sys.stderr, "ERROR: Can't import %s, skipping its tests:" % mod
            sys.excepthook(*sys.exc_info())
        else:
            # if there's a suite defined, incorporate its contents
            try:
                suite = getattr(module, 'suite')
            except AttributeError:
                # Look for individual tests
                moduleTests = testLoader.loadTestsFromModule(module)
                # unittest.TestSuite.addTests() doesn't work as advertised,
                # as it can't load tests from another TestSuite, so we have
                # to cheat:
                testSuite.addTest(moduleTests)
                continue
            if type(suite) == types.FunctionType:
                testSuite.addTest(suite())
            elif type(suite) == types.InstanceType \
                  and isinstance(suite, unittest.TestSuite):
                testSuite.addTest(suite)
            else:
                raise AssertionError, "don't understand suite (%s)" % mod
    sys.path.pop(0)
    return testSuite

def path2mod(path):
    """Convert a file path to a dotted module name."""
    return path[:-3].replace(os.sep, '.')

def import_module(name):
    """Import a dotted-path module name, and return the final component."""
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def main(suite=None):
    """
    Shared `main` for any individual test_* file.

    suite -- TestSuite to run. If not specified, look for any globally defined
    tests and run them.
    """
    parseArgs()
    if suite is None:
        # Load any globally defined tests.
        suite = unittest.defaultTestLoader.loadTestsFromModule(
              __import__('__main__'))
    if debug:
        print >>sys.stderr, "Debug: Suite=%s" % suite
    testRunner = unittest.TextTestRunner(verbosity=verbosity)
    # run suites (if we were called from test_all) or suite...
    if type(suite) == type([]):
        for s in suite:
            testRunner.run(s)
    else:
        testRunner.run(suite)
