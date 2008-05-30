#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 3085 $
# Date: $Date: 2005-03-22 21:38:43 +0100 (Tue, 22 Mar 2005) $
# Copyright: This module has been placed in the public domain.

"""
Test module for the ViewList class from statemachine.py.
"""

import unittest
import sys
import re
from DocutilsTestSupport import statemachine


class ViewListTests(unittest.TestCase):

    a_list = list('abcdefg')
    b_list = list('AEIOU')
    c_list = list('XYZ')

    def setUp(self):
        self.a = statemachine.ViewList(self.a_list, 'a')
        self.b = statemachine.ViewList(self.b_list, 'b')
        self.c = statemachine.ViewList(self.c_list, 'c')

    def test_lists(self):
        self.assertEqual(self.a, self.a_list)
        self.assertEqual(str(self.a), str(self.a_list))
        self.assertEqual(self.b, self.b_list)
        self.assertEqual(self.c, self.c_list)
        self.assertEqual(self.a.items,
                         zip('a' * len(self.a_list), range(len(self.a_list))))

    def test_get_slice(self):
        a = self.a[1:-1]
        a_list = self.a_list[1:-1]
        self.assertEqual(a, a_list)
        self.assertEqual(a.items,
                         zip('a' * len(a_list), range(1, len(a_list) + 1)))
        self.assertEqual(a.parent, self.a)

    def test_set_slice(self):
        a = statemachine.ViewList(self.a[:])
        s = a[2:-2]
        s[2:2] = self.b
        s_list = self.a_list[2:-2]
        s_list[2:2] = self.b_list
        self.assertEqual(s, s_list)
        self.assertEqual(s, a[2:-2])
        self.assertEqual(s.items, a[2:-2].items)

    def test_del_slice(self):
        a = statemachine.ViewList(self.a[:])
        s = a[2:]
        s_list = self.a_list[2:]
        del s[3:5]
        del s_list[3:5]
        self.assertEqual(s, s_list)
        self.assertEqual(s, a[2:])
        self.assertEqual(s.items, a[2:].items)

    def test_insert(self):
        a_list = self.a_list[:]
        a_list.insert(2, 'Q')
        a_list[4:4] = self.b_list
        a = self.a[:]
        self.assert_(isinstance(a, statemachine.ViewList))
        a.insert(2, 'Q', 'runtime')
        a.insert(4, self.b)
        self.assertEqual(a, a_list)
        self.assertEqual(a.info(2), ('runtime', 0))
        self.assertEqual(a.info(5), ('b', 1))

    def test_append(self):
        a_list = self.a_list[:]
        a_list.append('Q')
        a_list.extend(self.b_list)
        a = statemachine.ViewList(self.a)
        a.append('Q', 'runtime')
        a.append(self.b)
        self.assertEqual(a, a_list)
        self.assertEqual(a.info(len(self.a)), ('runtime', 0))
        self.assertEqual(a.info(-2), ('b', len(self.b) - 2))

    def test_extend(self):
        a_list = self.a_list[:]
        a_list.extend(self.b_list)
        a = statemachine.ViewList(self.a)
        a.extend(self.b)
        self.assertEqual(a, a_list)
        self.assertEqual(a.info(len(self.a) + 1), ('b', 1))

    def test_view(self):
        a = statemachine.ViewList(self.a[:])
        a.insert(4, self.b)
        s = a[2:-2]
        s.insert(5, self.c)
        self.assertEqual(s, a[2:-2])
        self.assertEqual(s.items, a[2:-2].items)
        s.pop()
        self.assertEqual(s, a[2:-2])
        self.assertEqual(s.items, a[2:-2].items)
        s.remove('X')
        self.assertEqual(s, a[2:-2])
        self.assertEqual(s.items, a[2:-2].items)

    def test_trim(self):
        a = statemachine.ViewList(self.a[:])
        s = a[1:-1]
        s.trim_start(1)
        self.assertEquals(a, self.a)
        self.assertEquals(s, a[2:-1])
        s.trim_end(1)
        self.assertEquals(a, self.a)
        self.assertEquals(s, a[2:-2])

        
#         print
#         print a
#         print s
#         print a.items
#         print s.items


class StringList(unittest.TestCase):

    text = """\
This is some
example text.

    Here is some
    indented text.

Unindented text.
"""

    indented_string = """\
        a
      literal
           block"""


    def setUp(self):
        self.a_list = self.text.splitlines(1)
        self.a = statemachine.StringList(self.a_list, 'a')

    def test_trim_left(self):
        s = self.a[3:5]
        s.trim_left(4)
        self.assertEqual(s, [line.lstrip() for line in self.a_list[3:5]])

    def test_get_indented(self):
        self.assertEquals(self.a.get_indented(),
                          ([], 0, 0))
        block = statemachine.StringList(
            statemachine.string2lines(self.indented_string))
        self.assertEquals(block.get_indented(),
                          ([s[6:] for s in block], 6, 1))


if __name__ == '__main__':
    unittest.main()
