#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@python.org
# Revision: $Revision: 3184 $
# Date: $Date: 2005-04-07 21:36:11 +0200 (Thu, 07 Apr 2005) $
# Copyright: This module has been placed in the public domain.

"""
Tests for the "header" & "footer" directives.
"""

from __init__ import DocutilsTestSupport

def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

totest = {}

totest['headers'] = [
["""\
.. header:: a paragraph for the header
""",
"""\
<document source="test data">
    <decoration>
        <header>
            <paragraph>
                a paragraph for the header
"""],
["""\
.. header::
""",
"""\
<document source="test data">
    <decoration>
        <header>
            <paragraph>
                Problem with the "header" directive: no content supplied.
    <system_message level="2" line="1" source="test data" type="WARNING">
        <paragraph>
            Content block expected for the "header" directive; none found.
        <literal_block xml:space="preserve">
            .. header::
"""],
["""\
.. header:: first part of the header
.. header:: second part of the header
""",
"""\
<document source="test data">
    <decoration>
        <header>
            <paragraph>
                first part of the header
            <paragraph>
                second part of the header
"""],
]

totest['footers'] = [
["""\
.. footer:: a paragraph for the footer
""",
"""\
<document source="test data">
    <decoration>
        <footer>
            <paragraph>
                a paragraph for the footer
"""],
["""\
.. footer:: even if a footer is declared first
.. header:: the header appears first
""",
"""\
<document source="test data">
    <decoration>
        <header>
            <paragraph>
                the header appears first
        <footer>
            <paragraph>
                even if a footer is declared first
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
