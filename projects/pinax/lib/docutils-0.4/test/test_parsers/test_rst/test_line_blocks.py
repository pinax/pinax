#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@python.org
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

totest['line_blocks'] = [
["""\
| This is a line block.
| Line breaks are *preserved*.

| This is a second line block.

| This is a third.
""",
"""\
<document source="test data">
    <line_block>
        <line>
            This is a line block.
        <line>
            Line breaks are \n\
            <emphasis>
                preserved
            .
    <line_block>
        <line>
            This is a second line block.
    <line_block>
        <line>
            This is a third.
"""],
["""\
| In line blocks,
|     Initial indentation is *also* preserved.
""",
"""\
<document source="test data">
    <line_block>
        <line>
            In line blocks,
        <line_block>
            <line>
                Initial indentation is \n\
                <emphasis>
                    also
                 preserved.
"""],
["""\
| Individual lines in line blocks
  *may* wrap, as indicated by the lack of a vertical bar prefix.
| These are called "continuation lines".
""",
"""\
<document source="test data">
    <line_block>
        <line>
            Individual lines in line blocks
            <emphasis>
                may
             wrap, as indicated by the lack of a vertical bar prefix.
        <line>
            These are called "continuation lines".
"""],
["""\
| Inline markup in line blocks may also wrap *to
  continuation lines*.
| But not to following lines.
""",
"""\
<document source="test data">
    <line_block>
        <line>
            Inline markup in line blocks may also wrap \n\
            <emphasis>
                to
                continuation lines
            .
        <line>
            But not to following lines.
"""],
["""\
\\| This is not a line block.
The vertical bar is simply part of a paragraph.
""",
"""\
<document source="test data">
    <paragraph>
        | This is not a line block.
        The vertical bar is simply part of a paragraph.
"""],
["""\
| This line block is incomplete.
There should be a blank line before this paragraph.
""",
"""\
<document source="test data">
    <line_block>
        <line>
            This line block is incomplete.
    <system_message level="2" line="2" source="test data" type="WARNING">
        <paragraph>
            Line block ends without a blank line.
    <paragraph>
        There should be a blank line before this paragraph.
"""],
["""\
| This line block contains
|
| blank lines.
""",
"""\
<document source="test data">
    <line_block>
        <line>
            This line block contains
        <line>
        <line>
            blank lines.
"""],
["""\
| The blank lines in this block
|   \n\
|       \n\
| have bogus spaces.
""",
"""\
<document source="test data">
    <line_block>
        <line>
            The blank lines in this block
        <line>
        <line>
        <line>
            have bogus spaces.
"""],
["""\
| Initial indentation is also significant and preserved:
|
|     Indented 4 spaces
| Not indented
|   Indented 2 spaces
|     Indented 4 spaces
|  Only one space
|
|     Continuation lines may be indented less
  than their base lines.
""",
"""\
<document source="test data">
    <line_block>
        <line>
            Initial indentation is also significant and preserved:
        <line>
        <line_block>
            <line>
                Indented 4 spaces
        <line>
            Not indented
        <line_block>
            <line_block>
                <line>
                    Indented 2 spaces
                <line_block>
                    <line>
                        Indented 4 spaces
            <line>
                Only one space
            <line>
            <line_block>
                <line>
                    Continuation lines may be indented less
                    than their base lines.
"""],
["""\
|
| This block begins and ends with blank lines.
|
""",
"""\
<document source="test data">
    <line_block>
        <line>
        <line>
            This block begins and ends with blank lines.
        <line>
"""],
["""\
This is not
| a line block.
""",
"""\
<document source="test data">
    <paragraph>
        This is not
        | a line block.
"""],
["""\
|   The first line is indented.
|     The second line is more indented.
""",
"""\
<document source="test data">
    <line_block>
        <line>
            The first line is indented.
        <line_block>
            <line>
                The second line is more indented.
"""],
["""\
|     The first line is indented.
|   The second line is less indented.
""",
"""\
<document source="test data">
    <line_block>
        <line_block>
            <line>
                The first line is indented.
        <line>
            The second line is less indented.
"""],
["""\
|This is not
|a line block

| This is an
|incomplete line block.
""",
"""\
<document source="test data">
    <paragraph>
        <problematic ids="id2" refid="id1">
            |
        This is not
        <problematic ids="id4" refid="id3">
            |
        a line block
    <system_message backrefs="id2" ids="id1" level="2" line="1" source="test data" type="WARNING">
        <paragraph>
            Inline substitution_reference start-string without end-string.
    <system_message backrefs="id4" ids="id3" level="2" line="1" source="test data" type="WARNING">
        <paragraph>
            Inline substitution_reference start-string without end-string.
    <line_block>
        <line>
            This is an
    <system_message level="2" line="5" source="test data" type="WARNING">
        <paragraph>
            Line block ends without a blank line.
    <paragraph>
        <problematic ids="id6" refid="id5">
            |
        incomplete line block.
    <system_message backrefs="id6" ids="id5" level="2" line="5" source="test data" type="WARNING">
        <paragraph>
            Inline substitution_reference start-string without end-string.
"""],
["""\
| Inline markup *may not
| wrap* over several lines.
""",
"""\
<document source="test data">
    <line_block>
        <line>
            Inline markup \n\
            <problematic ids="id2" refid="id1">
                *
            may not
        <line>
            wrap* over several lines.
    <system_message backrefs="id2" ids="id1" level="2" line="1" source="test data" type="WARNING">
        <paragraph>
            Inline emphasis start-string without end-string.
"""],
["""\
| * Block level markup
| * is not recognized.
""",
"""\
<document source="test data">
    <line_block>
        <line>
            * Block level markup
        <line>
            * is not recognized.
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
