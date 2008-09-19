# -*- coding: utf-8 -*-
"""
    Test suite for the util module
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2006-2007 by Georg Brandl.
    :license: BSD, see LICENSE for more details.
"""

import unittest
import os

from pygments import util


class UtilTest(unittest.TestCase):

    def test_getoptions(self):
        raises = self.assertRaises
        equals = self.assertEquals

        equals(util.get_bool_opt({}, 'a', True), True)
        equals(util.get_bool_opt({}, 'a', 1), True)
        equals(util.get_bool_opt({}, 'a', 'true'), True)
        equals(util.get_bool_opt({}, 'a', 'no'), False)
        raises(util.OptionError, util.get_bool_opt, {}, 'a', [])
        raises(util.OptionError, util.get_bool_opt, {}, 'a', 'foo')

        equals(util.get_int_opt({}, 'a', 1), 1)
        raises(util.OptionError, util.get_int_opt, {}, 'a', [])
        raises(util.OptionError, util.get_int_opt, {}, 'a', 'bar')

        equals(util.get_list_opt({}, 'a', [1]), [1])
        equals(util.get_list_opt({}, 'a', '1 2'), ['1', '2'])
        raises(util.OptionError, util.get_list_opt, {}, 'a', 1)


    def test_docstring_headline(self):
        def f1():
            """
            docstring headline

            other text
            """
        def f2():
            """
            docstring
            headline

            other text
            """

        self.assertEquals(util.docstring_headline(f1), "docstring headline")
        self.assertEquals(util.docstring_headline(f2), "docstring headline")

    def test_analysator(self):
        class X(object):
            def analyse(text):
                return 0.5
            analyse = util.make_analysator(analyse)
        self.assertEquals(X.analyse(''), 0.5)

    def test_shebang_matches(self):
        self.assert_(util.shebang_matches('#!/usr/bin/env python', r'python(2\.\d)?'))
        self.assert_(util.shebang_matches('#!/usr/bin/python2.4', r'python(2\.\d)?'))
        self.assert_(util.shebang_matches('#!/usr/bin/startsomethingwith python',
                                          r'python(2\.\d)?'))
        self.assert_(util.shebang_matches('#!C:\\Python2.4\\Python.exe',
                                          r'python(2\.\d)?'))

        self.failIf(util.shebang_matches('#!/usr/bin/python-ruby', r'python(2\.\d)?'))
        self.failIf(util.shebang_matches('#!/usr/bin/python/ruby', r'python(2\.\d)?'))
        self.failIf(util.shebang_matches('#!', r'python'))

    def test_doctype_matches(self):
        self.assert_(util.doctype_matches('<!DOCTYPE html PUBLIC "a"> <html>',
                                          'html.*'))
        self.failIf(util.doctype_matches('<?xml ?> <DOCTYPE html PUBLIC "a"> <html>',
                                         'html.*'))
        self.assert_(util.html_doctype_matches(
            '<?xml ?><!DOCTYPE html PUBLIC  "-//W3C//DTD XHTML 1.0 Strict//EN">'))

    def test_xml(self):
        self.assert_(util.looks_like_xml(
            '<?xml ?><!DOCTYPE html PUBLIC  "-//W3C//DTD XHTML 1.0 Strict//EN">'))
        self.assert_(util.looks_like_xml('<html xmlns>abc</html>'))
        self.failIf(util.looks_like_xml('<html>'))

if __name__ == '__main__':
    unittest.main()
