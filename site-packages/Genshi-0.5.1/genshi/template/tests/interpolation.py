# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2008 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://genshi.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://genshi.edgewall.org/log/.

import doctest
import sys
import unittest

from genshi.core import TEXT
from genshi.template.base import TemplateSyntaxError, EXPR
from genshi.template.interpolation import interpolate


class InterpolateTestCase(unittest.TestCase):

    def test_interpolate_string(self):
        parts = list(interpolate('bla'))
        self.assertEqual(1, len(parts))
        self.assertEqual(TEXT, parts[0][0])
        self.assertEqual('bla', parts[0][1])

    def test_interpolate_simple(self):
        parts = list(interpolate('${bla}'))
        self.assertEqual(1, len(parts))
        self.assertEqual(EXPR, parts[0][0])
        self.assertEqual('bla', parts[0][1].source)

    def test_interpolate_escaped(self):
        parts = list(interpolate('$${bla}'))
        self.assertEqual(1, len(parts))
        self.assertEqual(TEXT, parts[0][0])
        self.assertEqual('${bla}', parts[0][1])

    def test_interpolate_dobuleescaped(self):
        parts = list(interpolate('$$${bla}'))
        self.assertEqual(2, len(parts))
        self.assertEqual(TEXT, parts[0][0])
        self.assertEqual('$', parts[0][1])
        self.assertEqual(EXPR, parts[1][0])
        self.assertEqual('bla', parts[1][1].source)

    def test_interpolate_short(self):
        parts = list(interpolate('$bla'))
        self.assertEqual(1, len(parts))
        self.assertEqual(EXPR, parts[0][0])
        self.assertEqual('bla', parts[0][1].source)

    def test_interpolate_short_escaped(self):
        parts = list(interpolate('$$bla'))
        self.assertEqual(1, len(parts))
        self.assertEqual(TEXT, parts[0][0])
        self.assertEqual('$bla', parts[0][1])

    def test_interpolate_short_escaped_2(self):
        parts = list(interpolate('my $$bla = 2'))
        self.assertEqual(1, len(parts))
        self.assertEqual(TEXT, parts[0][0])
        self.assertEqual('my $bla = 2', parts[0][1])

    def test_interpolate_short_doubleescaped(self):
        parts = list(interpolate('$$$bla'))
        self.assertEqual(2, len(parts))
        self.assertEqual(TEXT, parts[0][0])
        self.assertEqual('$', parts[0][1])
        self.assertEqual(EXPR, parts[1][0])
        self.assertEqual('bla', parts[1][1].source)

    def test_interpolate_short_starting_with_underscore(self):
        parts = list(interpolate('$_bla'))
        self.assertEqual(1, len(parts))
        self.assertEqual(EXPR, parts[0][0])
        self.assertEqual('_bla', parts[0][1].source)

    def test_interpolate_short_containing_underscore(self):
        parts = list(interpolate('$foo_bar'))
        self.assertEqual(1, len(parts))
        self.assertEqual(EXPR, parts[0][0])
        self.assertEqual('foo_bar', parts[0][1].source)

    def test_interpolate_short_starting_with_dot(self):
        parts = list(interpolate('$.bla'))
        self.assertEqual(1, len(parts))
        self.assertEqual(TEXT, parts[0][0])
        self.assertEqual('$.bla', parts[0][1])

    def test_interpolate_short_containing_dot(self):
        parts = list(interpolate('$foo.bar'))
        self.assertEqual(1, len(parts))
        self.assertEqual(EXPR, parts[0][0])
        self.assertEqual('foo.bar', parts[0][1].source)

    def test_interpolate_short_starting_with_digit(self):
        parts = list(interpolate('$0bla'))
        self.assertEqual(1, len(parts))
        self.assertEqual(TEXT, parts[0][0])
        self.assertEqual('$0bla', parts[0][1])

    def test_interpolate_short_containing_digit(self):
        parts = list(interpolate('$foo0'))
        self.assertEqual(1, len(parts))
        self.assertEqual(EXPR, parts[0][0])
        self.assertEqual('foo0', parts[0][1].source)

    def test_interpolate_short_starting_with_digit(self):
        parts = list(interpolate('$0bla'))
        self.assertEqual(1, len(parts))
        self.assertEqual(TEXT, parts[0][0])
        self.assertEqual('$0bla', parts[0][1])

    def test_interpolate_short_containing_digit(self):
        parts = list(interpolate('$foo0'))
        self.assertEqual(1, len(parts))
        self.assertEqual(EXPR, parts[0][0])
        self.assertEqual('foo0', parts[0][1].source)

    def test_interpolate_full_nested_brackets(self):
        parts = list(interpolate('${{1:2}}'))
        self.assertEqual(1, len(parts))
        self.assertEqual(EXPR, parts[0][0])
        self.assertEqual('{1:2}', parts[0][1].source)

    def test_interpolate_full_mismatched_brackets(self):
        try:
            list(interpolate('${{1:2}'))
        except TemplateSyntaxError, e:
            pass
        else:
            self.fail('Expected TemplateSyntaxError')

    def test_interpolate_quoted_brackets_1(self):
        parts = list(interpolate('${"}"}'))
        self.assertEqual(1, len(parts))
        self.assertEqual(EXPR, parts[0][0])
        self.assertEqual('"}"', parts[0][1].source)

    def test_interpolate_quoted_brackets_2(self):
        parts = list(interpolate("${'}'}"))
        self.assertEqual(1, len(parts))
        self.assertEqual(EXPR, parts[0][0])
        self.assertEqual("'}'", parts[0][1].source)

    def test_interpolate_quoted_brackets_3(self):
        parts = list(interpolate("${'''}'''}"))
        self.assertEqual(1, len(parts))
        self.assertEqual(EXPR, parts[0][0])
        self.assertEqual("'''}'''", parts[0][1].source)

    def test_interpolate_quoted_brackets_4(self):
        parts = list(interpolate("${'''}\"\"\"'''}"))
        self.assertEqual(1, len(parts))
        self.assertEqual(EXPR, parts[0][0])
        self.assertEqual("'''}\"\"\"'''", parts[0][1].source)

    def test_interpolate_quoted_brackets_5(self):
        parts = list(interpolate(r"${'\'}'}"))
        self.assertEqual(1, len(parts))
        self.assertEqual(EXPR, parts[0][0])
        self.assertEqual(r"'\'}'", parts[0][1].source)

    def test_interpolate_mixed1(self):
        parts = list(interpolate('$foo bar $baz'))
        self.assertEqual(3, len(parts))
        self.assertEqual(EXPR, parts[0][0])
        self.assertEqual('foo', parts[0][1].source)
        self.assertEqual(TEXT, parts[1][0])
        self.assertEqual(' bar ', parts[1][1])
        self.assertEqual(EXPR, parts[2][0])
        self.assertEqual('baz', parts[2][1].source)

    def test_interpolate_mixed2(self):
        parts = list(interpolate('foo $bar baz'))
        self.assertEqual(3, len(parts))
        self.assertEqual(TEXT, parts[0][0])
        self.assertEqual('foo ', parts[0][1])
        self.assertEqual(EXPR, parts[1][0])
        self.assertEqual('bar', parts[1][1].source)
        self.assertEqual(TEXT, parts[2][0])
        self.assertEqual(' baz', parts[2][1])

    def test_interpolate_triplequoted(self):
        parts = list(interpolate('${"""foo\nbar"""}'))
        self.assertEqual(1, len(parts))
        self.assertEqual('"""foo\nbar"""', parts[0][1].source)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(interpolate.__module__))
    suite.addTest(unittest.makeSuite(InterpolateTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
