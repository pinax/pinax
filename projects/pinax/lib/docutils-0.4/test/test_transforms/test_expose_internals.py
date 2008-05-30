#! /usr/bin/env python

# Author: Felix Wiemann
# Contact: Felix_Wiemann@ososo.de
# Revision: $Revision: 4132 $
# Date: $Date: 2005-12-03 03:13:12 +0100 (Sat, 03 Dec 2005) $
# Copyright: This module has been placed in the public domain.

"""
Test module for universal.ExposeInternals transform.
"""


from __init__ import DocutilsTestSupport # must be imported before docutils
from docutils.transforms.universal import ExposeInternals
from docutils.parsers.rst import Parser

def suite():
    parser = Parser()
    s = DocutilsTestSupport.TransformTestSuite(
        parser, suite_settings={'expose_internals': ['rawsource', 'source']})
    s.generateTests(totest)
    return s


totest = {}

totest['transitions'] = ((ExposeInternals,), [
["""\
This is a test.
""",
"""\
<document internal:rawsource="" source="test data">
    <paragraph internal:rawsource="This is a test." internal:source="test data">
        This is a test.
"""],
])


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
