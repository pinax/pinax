#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 778 $
# Date: $Date: 2002-10-09 02:51:53 +0200 (Wed, 09 Oct 2002) $
# Copyright: This module has been placed in the public domain.

"""
Tests for states.py.
"""

import unittest
from __init__ import DocutilsTestSupport
states = DocutilsTestSupport.states


class FuctionTests(unittest.TestCase):

    escaped = r'escapes: \*one, \\*two, \\\*three'
    nulled = 'escapes: \x00*one, \x00\\*two, \x00\\\x00*three'
    unescaped = r'escapes: *one, \*two, \*three'

    def test_escape2null(self):
        nulled = states.escape2null(self.escaped)
        self.assertEquals(nulled, self.nulled)
        nulled = states.escape2null(self.escaped + '\\')
        self.assertEquals(nulled, self.nulled + '\x00')

    def test_unescape(self):
        unescaped = states.unescape(self.nulled)
        self.assertEquals(unescaped, self.unescaped)
        restored = states.unescape(self.nulled, 1)
        self.assertEquals(restored, self.escaped)


if __name__ == '__main__':
    unittest.main()
