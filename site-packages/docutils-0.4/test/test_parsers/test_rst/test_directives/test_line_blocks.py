#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@python.org
# Revision: $Revision: 3129 $
# Date: $Date: 2005-03-26 17:21:28 +0100 (Sat, 26 Mar 2005) $
# Copyright: This module has been placed in the public domain.

"""
Tests for the body.py 'line-block' directive.
"""

from __init__ import DocutilsTestSupport

def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

totest = {}

totest['line_blocks'] = [
["""\
.. line-block::

   This is a line block.
   Newlines are *preserved*.
       As is initial whitespace.
""",
"""\
<document source="test data">
    <line_block>
        <line>
            This is a line block.
        <line>
            Newlines are \n\
            <emphasis>
                preserved
            .
        <line_block>
            <line>
                As is initial whitespace.
"""],
["""\
.. line-block::

   Inline markup *may not span
       multiple lines* of a line block.
""",
"""\
<document source="test data">
    <line_block>
        <line>
            Inline markup \n\
            <problematic ids="id2" refid="id1">
                *
            may not span
        <line_block>
            <line>
                multiple lines* of a line block.
    <system_message backrefs="id2" ids="id1" level="2" line="3" source="test data" type="WARNING">
        <paragraph>
            Inline emphasis start-string without end-string.
"""],
["""\
.. line-block::
""",
"""\
<document source="test data">
    <system_message level="2" line="1" source="test data" type="WARNING">
        <paragraph>
            Content block expected for the "line-block" directive; none found.
        <literal_block xml:space="preserve">
            .. line-block::
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
