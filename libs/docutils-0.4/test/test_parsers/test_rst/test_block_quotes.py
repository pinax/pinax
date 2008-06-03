#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 4147 $
# Date: $Date: 2005-12-06 02:06:33 +0100 (Tue, 06 Dec 2005) $
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

totest['block_quotes'] = [
["""\
Line 1.
Line 2.

   Indented.
""",
"""\
<document source="test data">
    <paragraph>
        Line 1.
        Line 2.
    <block_quote>
        <paragraph>
            Indented.
"""],
["""\
Line 1.
Line 2.

   Indented 1.

      Indented 2.
""",
"""\
<document source="test data">
    <paragraph>
        Line 1.
        Line 2.
    <block_quote>
        <paragraph>
            Indented 1.
        <block_quote>
            <paragraph>
                Indented 2.
"""],
["""\
Line 1.
Line 2.
    Unexpectedly indented.
""",
"""\
<document source="test data">
    <paragraph>
        Line 1.
        Line 2.
    <system_message level="3" line="3" source="test data" type="ERROR">
        <paragraph>
            Unexpected indentation.
    <block_quote>
        <paragraph>
            Unexpectedly indented.
"""],
["""\
Line 1.
Line 2.

   Indented.
no blank line
""",
"""\
<document source="test data">
    <paragraph>
        Line 1.
        Line 2.
    <block_quote>
        <paragraph>
            Indented.
    <system_message level="2" line="5" source="test data" type="WARNING">
        <paragraph>
            Block quote ends without a blank line; unexpected unindent.
    <paragraph>
        no blank line
"""],
["""\
Here is a paragraph.

        Indent 8 spaces.

    Indent 4 spaces.

Is this correct? Should it generate a warning?
Yes, it is correct, no warning necessary.
""",
"""\
<document source="test data">
    <paragraph>
        Here is a paragraph.
    <block_quote>
        <block_quote>
            <paragraph>
                Indent 8 spaces.
        <paragraph>
            Indent 4 spaces.
    <paragraph>
        Is this correct? Should it generate a warning?
        Yes, it is correct, no warning necessary.
"""],
["""\
Paragraph.

   Block quote.

   -- Attribution

Paragraph.

   Block quote.

   --Attribution
""",
"""\
<document source="test data">
    <paragraph>
        Paragraph.
    <block_quote>
        <paragraph>
            Block quote.
        <attribution>
            Attribution
    <paragraph>
        Paragraph.
    <block_quote>
        <paragraph>
            Block quote.
        <attribution>
            Attribution
"""],
[u"""\
Alternative: true em-dash.

   Block quote.

   \u2014 Attribution

Alternative: three hyphens.

   Block quote.

   --- Attribution
""",
"""\
<document source="test data">
    <paragraph>
        Alternative: true em-dash.
    <block_quote>
        <paragraph>
            Block quote.
        <attribution>
            Attribution
    <paragraph>
        Alternative: three hyphens.
    <block_quote>
        <paragraph>
            Block quote.
        <attribution>
            Attribution
"""],
["""\
Paragraph.

   Block quote.

   -- Attribution line one
   and line two

Paragraph.

   Block quote.

   -- Attribution line one
      and line two

Paragraph.
""",
"""\
<document source="test data">
    <paragraph>
        Paragraph.
    <block_quote>
        <paragraph>
            Block quote.
        <attribution>
            Attribution line one
            and line two
    <paragraph>
        Paragraph.
    <block_quote>
        <paragraph>
            Block quote.
        <attribution>
            Attribution line one
            and line two
    <paragraph>
        Paragraph.
"""],
["""\
Paragraph.

   -- Not an attribution

Paragraph.

   Block quote.

   \-- Not an attribution

Paragraph.

   Block quote.

   -- Not an attribution line one
      and line two
          and line three
""",
"""\
<document source="test data">
    <paragraph>
        Paragraph.
    <block_quote>
        <paragraph>
            -- Not an attribution
    <paragraph>
        Paragraph.
    <block_quote>
        <paragraph>
            Block quote.
        <paragraph>
            -- Not an attribution
    <paragraph>
        Paragraph.
    <block_quote>
        <paragraph>
            Block quote.
        <definition_list>
            <definition_list_item>
                <term>
                    -- Not an attribution line one
                <definition>
                    <definition_list>
                        <definition_list_item>
                            <term>
                                and line two
                            <definition>
                                <paragraph>
                                    and line three
"""],
]

if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
