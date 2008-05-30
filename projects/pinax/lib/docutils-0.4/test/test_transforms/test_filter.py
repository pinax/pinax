#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 3085 $
# Date: $Date: 2005-03-22 21:38:43 +0100 (Tue, 22 Mar 2005) $
# Copyright: This module has been placed in the public domain.

"""
Tests for docutils.transforms.components.Filter.
"""

from __init__ import DocutilsTestSupport
from docutils.parsers.rst import Parser


def suite():
    parser = Parser()
    s = DocutilsTestSupport.TransformTestSuite(parser)
    s.generateTests(totest)
    return s

totest = {}

totest['meta'] = ((), [
["""\
.. meta::
   :description: The reStructuredText plaintext markup language
   :keywords: plaintext,markup language
""",
"""\
<document source="test data">
    <meta content="The reStructuredText plaintext markup language" name="description">
    <meta content="plaintext,markup language" name="keywords">
"""],
])


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
