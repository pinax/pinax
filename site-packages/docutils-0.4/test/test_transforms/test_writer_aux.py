#! /usr/bin/env python

# Author: Felix Wiemann
# Contact: Felix_Wiemann@ososo.de
# Revision: $Revision: 4132 $
# Date: $Date: 2005-12-03 03:13:12 +0100 (Sat, 03 Dec 2005) $
# Copyright: This module has been placed in the public domain.

"""
Test module for writer_aux transforms.
"""

from __init__ import DocutilsTestSupport # must be imported before docutils
from docutils.transforms import writer_aux
from docutils.parsers.rst import Parser

def suite():
    parser = Parser()
    s = DocutilsTestSupport.TransformTestSuite(parser)
    s.generateTests(totest)
    return s


totest = {}

totest['compound'] = ((writer_aux.Compound,), [
["""\
.. class:: compound

.. compound::

   .. class:: paragraph1

   Paragraph 1.

   .. class:: paragraph2

   Paragraph 2.

       Block quote.
""",
"""\
<document source="test data">
    <paragraph classes="paragraph1 compound">
        Paragraph 1.
    <paragraph classes="paragraph2 continued">
        Paragraph 2.
    <block_quote classes="continued">
        <paragraph>
            Block quote.
"""],
])


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
