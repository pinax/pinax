#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 3085 $
# Date: $Date: 2005-03-22 21:38:43 +0100 (Tue, 22 Mar 2005) $
# Copyright: This module has been placed in the public domain.

"""
Tests for PySource Reader functions.
"""

import unittest
from __init__ import DocutilsTestSupport
from docutils.readers.python.moduleparser import trim_docstring


class MiscTests(unittest.TestCase):

    docstrings = (
        ("""""", """"""), # empty
        ("""Begins on the first line.

        Middle line indented.

    Last line unindented.
    """,
         """\
Begins on the first line.

    Middle line indented.

Last line unindented."""),
        ("""
    Begins on the second line.

        Middle line indented.

    Last line unindented.""",
         """\
Begins on the second line.

    Middle line indented.

Last line unindented."""),
        ("""All on one line.""", """All on one line."""))

    def test_trim_docstring(self):
        for docstring, expected in self.docstrings:
            self.assertEquals(trim_docstring(docstring), expected)
            self.assertEquals(trim_docstring('\n    ' + docstring),
                              expected)


if __name__ == '__main__':
    unittest.main()
