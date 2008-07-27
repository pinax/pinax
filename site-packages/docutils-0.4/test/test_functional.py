#!/usr/bin/env python

# Author: Felix Wiemann
# Contact: Felix_Wiemann@ososo.de
# Revision: $Revision: 4254 $
# Date: $Date: 2006-01-09 04:06:58 +0100 (Mon, 09 Jan 2006) $
# Copyright: This module has been placed in the public domain.

"""
Perform tests with the data in the functional/ directory.

Read README.txt for details on how this is done.
"""

import sys
import os
import os.path
import shutil
import unittest
import difflib
import DocutilsTestSupport              # must be imported before docutils
import docutils
import docutils.core


datadir = 'functional'
"""The directory to store the data needed for the functional tests."""


def join_path(*args):
    return '/'.join(args) or '.'


class FunctionalTestSuite(DocutilsTestSupport.CustomTestSuite):

    """Test suite containing test cases for all config files."""

    def __init__(self):
        """Process all config files in functional/tests/."""
        DocutilsTestSupport.CustomTestSuite.__init__(self)
        os.chdir(DocutilsTestSupport.testroot)
        self.clear_output_directory()
        self.added = 0
        os.path.walk(join_path(datadir, 'tests'), self.walker, None)
        assert self.added, 'No functional tests found.'

    def clear_output_directory(self):
        files = os.listdir(os.path.join('functional', 'output'))
        for f in files:
            if f in ('README.txt', '.svn', 'CVS'):
                continue                # don't touch the infrastructure
            path = os.path.join('functional', 'output', f)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

    def walker(self, dummy, dirname, names):
        """
        Process all config files among `names` in `dirname`.

        This is a helper function for os.path.walk.  A config file is
        a Python file (*.py) which sets several variables.
        """
        for name in names:
            if name.endswith('.py') and not name.startswith('_'):
                config_file_full_path = join_path(dirname, name)
                self.addTestCase(FunctionalTestCase, 'test', None, None,
                                 id=config_file_full_path,
                                 configfile=config_file_full_path)
                self.added += 1


class FunctionalTestCase(DocutilsTestSupport.CustomTestCase):

    """Test case for one config file."""

    def __init__(self, *args, **kwargs):
        """Set self.configfile, pass arguments to parent __init__."""
        self.configfile = kwargs['configfile']
        del kwargs['configfile']
        DocutilsTestSupport.CustomTestCase.__init__(self, *args, **kwargs)

    def shortDescription(self):
        return 'test_functional.py: ' + self.configfile

    def test(self):
        """Process self.configfile."""
        os.chdir(DocutilsTestSupport.testroot)
        # Keyword parameters for publish_file:
        namespace = {}
        # Initialize 'settings_overrides' for test settings scripts,
        # and disable configuration files:
        namespace['settings_overrides'] = {'_disable_config': 1}
        # Read the variables set in the default config file and in
        # the current config file into namespace:
        execfile(join_path(datadir, 'tests', '_default.py'), namespace)
        execfile(self.configfile, namespace)
        # Check for required settings:
        assert namespace.has_key('test_source'),\
               "No 'test_source' supplied in " + self.configfile
        assert namespace.has_key('test_destination'),\
               "No 'test_destination' supplied in " + self.configfile
        # Set source_path and destination_path if not given:
        namespace.setdefault('source_path',
                             join_path(datadir, 'input',
                                       namespace['test_source']))
        # Path for actual output:
        namespace.setdefault('destination_path',
                             join_path(datadir, 'output',
                                       namespace['test_destination']))
        # Path for expected output:
        expected_path = join_path(datadir, 'expected',
                                  namespace['test_destination'])
        # shallow copy of namespace to minimize:
        params = namespace.copy()
        # remove unneeded parameters:
        del params['test_source']
        del params['test_destination']
        # Delete private stuff like params['__builtins__']:
        for key in params.keys():
            if key.startswith('_'):
                del params[key]
        # Get output (automatically written to the output/ directory
        # by publish_file):
        output = docutils.core.publish_file(**params)
        # Get the expected output *after* writing the actual output.
        self.assert_(os.access(expected_path, os.R_OK),\
                     'Cannot find expected output at\n' + expected_path)
        f = open(expected_path, 'rU')
        expected = f.read()
        f.close()
        diff = ('The expected and actual output differs.\n'
                'Please compare the expected and actual output files:\n'
                '  diff %s %s\n'
                'If the actual output is correct, please replace the\n'
                'expected output and check it in to Subversion:\n'
                '  mv %s %s\n'
                '  svn commit -m "<comment>" %s'
                % (expected_path, params['destination_path'],
                   params['destination_path'], expected_path, expected_path))
        try:
            self.assertEquals(output, expected, diff)
        except AssertionError:
            if hasattr(difflib, 'unified_diff'):
                # Generate diff if unified_diff available:
                diff = ''.join(
                    difflib.unified_diff(expected.splitlines(1),
                                         output.splitlines(1),
                                         expected_path,
                                         params['destination_path']))
            print >>sys.stderr, '\n%s:' % (self,)
            print >>sys.stderr, diff
            raise
        # Execute optional function containing extra tests:
        if namespace.has_key('_test_more'):
            namespace['_test_more'](join_path(datadir, 'expected'),
                                    join_path(datadir, 'output'),
                                    self, namespace)


def suite():
    return FunctionalTestSuite()


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
