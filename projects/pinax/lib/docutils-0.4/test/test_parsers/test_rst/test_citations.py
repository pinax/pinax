#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 3129 $
# Date: $Date: 2005-03-26 17:21:28 +0100 (Sat, 26 Mar 2005) $
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

totest['citations'] = [
["""\
.. [citation] This is a citation.
""",
"""\
<document source="test data">
    <citation ids="citation" names="citation">
        <label>
            citation
        <paragraph>
            This is a citation.
"""],
["""\
.. [citation1234] This is a citation with year.
""",
"""\
<document source="test data">
    <citation ids="citation1234" names="citation1234">
        <label>
            citation1234
        <paragraph>
            This is a citation with year.
"""],
["""\
.. [citation] This is a citation
   on multiple lines.
""",
"""\
<document source="test data">
    <citation ids="citation" names="citation">
        <label>
            citation
        <paragraph>
            This is a citation
            on multiple lines.
"""],
["""\
.. [citation1] This is a citation
     on multiple lines with more space.

.. [citation2] This is a citation
  on multiple lines with less space.
""",
"""\
<document source="test data">
    <citation ids="citation1" names="citation1">
        <label>
            citation1
        <paragraph>
            This is a citation
            on multiple lines with more space.
    <citation ids="citation2" names="citation2">
        <label>
            citation2
        <paragraph>
            This is a citation
            on multiple lines with less space.
"""],
["""\
.. [citation]
   This is a citation on multiple lines
   whose block starts on line 2.
""",
"""\
<document source="test data">
    <citation ids="citation" names="citation">
        <label>
            citation
        <paragraph>
            This is a citation on multiple lines
            whose block starts on line 2.
"""],
["""\
.. [citation]

That was an empty citation.
""",
"""\
<document source="test data">
    <citation ids="citation" names="citation">
        <label>
            citation
    <paragraph>
        That was an empty citation.
"""],
["""\
.. [citation]
No blank line.
""",
"""\
<document source="test data">
    <citation ids="citation" names="citation">
        <label>
            citation
    <system_message level="2" line="2" source="test data" type="WARNING">
        <paragraph>
            Explicit markup ends without a blank line; unexpected unindent.
    <paragraph>
        No blank line.
"""],
["""\
.. [citation label with spaces] this isn't a citation

.. [*citationlabelwithmarkup*] this isn't a citation
""",
"""\
<document source="test data">
    <comment xml:space="preserve">
        [citation label with spaces] this isn't a citation
    <comment xml:space="preserve">
        [*citationlabelwithmarkup*] this isn't a citation
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
