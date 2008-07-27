#! /usr/bin/env python

# Author: Felix Wiemann
# Contact: Felix_Wiemann@ososo.de
# Revision: $Revision: 4132 $
# Date: $Date: 2005-12-03 03:13:12 +0100 (Sat, 03 Dec 2005) $
# Copyright: This module has been placed in the public domain.

"""
Test module for io.py.
"""

import unittest
import DocutilsTestSupport              # must be imported before docutils
from docutils import io


class InputTests(unittest.TestCase):

    def test_bom(self):
        input = io.StringInput(source='\xef\xbb\xbf foo \xef\xbb\xbf bar',
                               encoding='utf8')
        # Assert BOMs are gone.
        self.assertEquals(input.read(), u' foo  bar')
        # With unicode input:
        input = io.StringInput(source=u'\ufeff foo \ufeff bar')
        # Assert BOMs are still there.
        self.assertEquals(input.read(), u'\ufeff foo \ufeff bar')


if __name__ == '__main__':
    unittest.main()
