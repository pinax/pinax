# -*- coding: utf-8 -*-
#
# Copyright (C) 2006 Edgewall Software
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
import unittest

from genshi import util
from genshi.util import LRUCache


class LRUCacheTestCase(unittest.TestCase):

    def test_setitem(self):
        cache = LRUCache(2)
        cache['A'] = 0
        self.assertEqual(1, len(cache))
        self.assertEqual('A', cache.head.key)
        self.assertEqual('A', cache.tail.key)
        item_a = cache._dict['A']
        self.assertEqual('A', item_a.key)
        self.assertEqual(0, item_a.value)
        self.assertEqual(None, item_a.previous)
        self.assertEqual(None, item_a.next)

        cache['B'] = 1
        self.assertEqual(2, len(cache))
        self.assertEqual('B', cache.head.key)
        self.assertEqual('A', cache.tail.key)
        item_a = cache._dict['A']
        item_b = cache._dict['B']
        self.assertEqual('A', item_a.key)
        self.assertEqual(0, item_a.value)
        self.assertEqual(item_b, item_a.previous)
        self.assertEqual(None, item_a.next)
        self.assertEqual('B', item_b.key)
        self.assertEqual(1, item_b.value)
        self.assertEqual(None, item_b.previous)
        self.assertEqual(item_a, item_b.next)

        cache['C'] = 2
        self.assertEqual(2, len(cache))
        self.assertEqual('C', cache.head.key)
        self.assertEqual('B', cache.tail.key)
        item_b = cache._dict['B']
        item_c = cache._dict['C']
        self.assertEqual('B', item_b.key)
        self.assertEqual(1, item_b.value)
        self.assertEqual(item_c, item_b.previous)
        self.assertEqual(None, item_b.next)
        self.assertEqual('C', item_c.key)
        self.assertEqual(2, item_c.value)
        self.assertEqual(None, item_c.previous)
        self.assertEqual(item_b, item_c.next)

    def test_getitem(self):
        cache = LRUCache(2)
        cache['A'] = 0
        cache['B'] = 1

        cache['A']

        self.assertEqual(2, len(cache))
        self.assertEqual('A', cache.head.key)
        self.assertEqual('B', cache.tail.key)
        item_a = cache._dict['A']
        item_b = cache._dict['B']
        self.assertEqual('A', item_a.key)
        self.assertEqual(0, item_a.value)
        self.assertEqual(None, item_a.previous)
        self.assertEqual(item_b, item_a.next)
        self.assertEqual('B', item_b.key)
        self.assertEqual(1, item_b.value)
        self.assertEqual(item_a, item_b.previous)
        self.assertEqual(None, item_b.next)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(util))
    suite.addTest(unittest.makeSuite(LRUCacheTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
