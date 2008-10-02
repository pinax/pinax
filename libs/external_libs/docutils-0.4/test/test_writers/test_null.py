#!/usr/bin/env python

# Author: Felix Wiemann
# Contact: Felix_Wiemann@ososo.de
# Revision: $Revision: 3646 $
# Date: $Date: 2005-07-03 01:08:53 +0200 (Sun, 03 Jul 2005) $
# Copyright: This module has been placed in the public domain.

"""
Test for Null writer.
"""

from __init__ import DocutilsTestSupport

def suite():
    s = DocutilsTestSupport.PublishTestSuite('null')
    s.generateTests(totest)
    return s

totest = {}

totest['basic'] = [
["""\
This is a paragraph.
""",
None]
]

if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
