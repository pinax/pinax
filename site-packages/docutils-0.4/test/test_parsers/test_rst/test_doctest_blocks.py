#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 778 $
# Date: $Date: 2002-10-09 02:51:53 +0200 (Wed, 09 Oct 2002) $
# Copyright: This module has been placed in the public domain.

"""
Tests for states.py.
"""

from __init__ import DocutilsTestSupport

def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

totest = {}

totest['doctest_blocks'] = [
["""\
Paragraph.

>>> print "Doctest block."
Doctest block.

Paragraph.
""",
"""\
<document source="test data">
    <paragraph>
        Paragraph.
    <doctest_block xml:space="preserve">
        >>> print "Doctest block."
        Doctest block.
    <paragraph>
        Paragraph.
"""],
["""\
Paragraph.

>>> print "    Indented output."
    Indented output.
""",
"""\
<document source="test data">
    <paragraph>
        Paragraph.
    <doctest_block xml:space="preserve">
        >>> print "    Indented output."
            Indented output.
"""],
["""\
Paragraph.

    >>> print "    Indented block & output."
        Indented block & output.
""",
"""\
<document source="test data">
    <paragraph>
        Paragraph.
    <block_quote>
        <doctest_block xml:space="preserve">
            >>> print "    Indented block & output."
                Indented block & output.
"""],
]

if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
