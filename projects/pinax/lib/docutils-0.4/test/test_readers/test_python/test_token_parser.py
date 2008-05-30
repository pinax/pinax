#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 3085 $
# Date: $Date: 2005-03-22 21:38:43 +0100 (Tue, 22 Mar 2005) $
# Copyright: This module has been placed in the public domain.

"""
Tests for docutils/readers/python/moduleparser.py.
"""

from __init__ import DocutilsTestSupport


def suite():
    s = DocutilsTestSupport.PythonModuleParserTestSuite()
    s.generateTests(totest, testmethod='test_token_parser_rhs')
    return s

totest = {}

totest['expressions'] = [
['''a = 1''', '''1'''],
['''a = b = 1''', '''1'''],
['''\
a = (
     1 + 2
     + 3
     )
''',
'''(1 + 2 + 3)'''],
['''\
a = """\\
line one
line two"""
''',
'''"""\\\nline one\nline two"""'''],
['''a = `1`''', '''`1`'''],
['''a = `1`+`2`''', '''`1` + `2`'''],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
