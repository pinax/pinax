#!/usr/bin/env python

# Author: David Goodger
# Contact: goodger@python.org
# Revision:  $Revision: 4222 $
# Date:      $Date: 2005-12-16 00:47:54 +0100 (Fri, 16 Dec 2005) $
# Copyright: This module has been placed in the public domain.

"""
Tests of runtime settings.
"""

import sys
import os
import docutils_difflib
import pprint
import warnings
import unittest
from types import StringType
import DocutilsTestSupport              # must be imported before docutils
from docutils import frontend, utils
from docutils.writers import html4css1, pep_html
from docutils.parsers import rst


warnings.filterwarnings(action='ignore',
                        category=frontend.ConfigDeprecationWarning)

def fixpath(path):
    return os.path.abspath(os.path.join(*(path.split('/'))))


class ConfigFileTests(unittest.TestCase):

    config_files = {'old': fixpath('data/config_old.txt'),
                    'one': fixpath('data/config_1.txt'),
                    'two': fixpath('data/config_2.txt'),
                    'list': fixpath('data/config_list.txt'),
                    'list2': fixpath('data/config_list_2.txt'),
                    'error': fixpath('data/config_error_handler.txt')}

    settings = {
        'old': {'datestamp': '%Y-%m-%d %H:%M UTC',
                'generator': 1,
                'no_random': 1,
                'python_home': 'http://www.python.org',
                'source_link': 1,
                'stylesheet': None,
                'stylesheet_path': fixpath('data/stylesheets/pep.css'),
                'template': fixpath('data/pep-html-template')},
        'one': {'datestamp': '%Y-%m-%d %H:%M UTC',
                'generator': 1,
                'no_random': 1,
                'python_home': 'http://www.python.org',
                'record_dependencies': utils.DependencyList(),
                'source_link': 1,
                'stylesheet': None,
                'stylesheet_path': fixpath('data/stylesheets/pep.css'),
                'tab_width': 8,
                'template': fixpath('data/pep-html-template'),
                'trim_footnote_reference_space': 1},
        'two': {'footnote_references': 'superscript',
                'generator': 0,
                'record_dependencies': utils.DependencyList(),
                'stylesheet': None,
                'stylesheet_path': fixpath('data/test.css'),
                'trim_footnote_reference_space': None},
        'list': {'expose_internals': ['a', 'b', 'c', 'd', 'e']},
        'list2': {'expose_internals': ['a', 'b', 'c', 'd', 'e', 'f']},
        'error': {'error_encoding': 'ascii',
                  'error_encoding_error_handler': 'strict'},
        }

    compare = docutils_difflib.Differ().compare
    """Comparison method shared by all tests."""

    def setUp(self):
        self.option_parser = frontend.OptionParser(
            components=(pep_html.Writer, rst.Parser), read_config_files=None)

    def files_settings(self, *names):
        settings = frontend.Values()
        for name in names:
            settings.update(self.option_parser.get_config_file_settings(
                self.config_files[name]), self.option_parser)
        return settings.__dict__

    def expected_settings(self, *names):
        expected = {}
        for name in names:
            expected.update(self.settings[name])
        return expected

    def compare_output(self, result, expected):
        """`result` and `expected` should both be dicts."""
        self.assert_(result.has_key('record_dependencies'))
        if not expected.has_key('record_dependencies'):
            # Delete it if we don't want to test it.
            del result['record_dependencies']
        result = pprint.pformat(result) + '\n'
        expected = pprint.pformat(expected) + '\n'
        try:
            self.assertEquals(result, expected)
        except AssertionError:
            print >>sys.stderr, '\n%s\n' % (self,)
            print >>sys.stderr, '-: expected\n+: result'
            print >>sys.stderr, ''.join(self.compare(expected.splitlines(1),
                                                     result.splitlines(1)))
            raise

    def test_nofiles(self):
        self.compare_output(self.files_settings(),
                            self.expected_settings())

    def test_old(self):
        self.compare_output(self.files_settings('old'),
                            self.expected_settings('old'))

    def test_one(self):
        self.compare_output(self.files_settings('one'),
                            self.expected_settings('one'))

    def test_multiple(self):
        self.compare_output(self.files_settings('one', 'two'),
                            self.expected_settings('one', 'two'))

    def test_old_and_new(self):
        self.compare_output(self.files_settings('old', 'two'),
                            self.expected_settings('old', 'two'))

    def test_list(self):
        self.compare_output(self.files_settings('list'),
                            self.expected_settings('list'))

    def test_list2(self):
        self.compare_output(self.files_settings('list', 'list2'),
                            self.expected_settings('list2'))

    def test_error_handler(self):
        self.compare_output(self.files_settings('error'),
                            self.expected_settings('error'))


class ConfigEnvVarFileTests(ConfigFileTests):

    """
    Repeats the tests of `ConfigFileTests` using the ``DOCUTILSCONFIG``
    environment variable and the standard Docutils config file mechanism.
    """

    def setUp(self):
        ConfigFileTests.setUp(self)
        self.orig_environ = os.environ
        os.environ = os.environ.copy()

    def files_settings(self, *names):
        files = [self.config_files[name] for name in names]
        os.environ['DOCUTILSCONFIG'] = os.pathsep.join(files)
        settings = self.option_parser.get_standard_config_settings()
        return settings.__dict__

    def tearDown(self):
        os.environ = self.orig_environ


if __name__ == '__main__':
    unittest.main()
