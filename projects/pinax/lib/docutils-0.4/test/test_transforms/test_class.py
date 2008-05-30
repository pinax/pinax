#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 3915 $
# Date: $Date: 2005-10-02 03:06:42 +0200 (Sun, 02 Oct 2005) $
# Copyright: This module has been placed in the public domain.

"""
Tests for `docutils.transforms.misc.ClassAttribute`.
"""

from __init__ import DocutilsTestSupport
from docutils.parsers.rst import Parser


def suite():
    parser = Parser()
    s = DocutilsTestSupport.TransformTestSuite(parser)
    s.generateTests(totest)
    return s

totest = {}

totest['class'] = ((), [
["""\
.. class:: one

paragraph
""",
"""\
<document source="test data">
    <paragraph classes="one">
        paragraph
"""],
["""\
.. class:: two
..

    Block quote
""",
"""\
<document source="test data">
    <comment xml:space="preserve">
    <block_quote classes="two">
        <paragraph>
            Block quote
"""],
["""\
    Block quote

    .. class:: three

Paragraph
""",
"""\
<document source="test data">
    <block_quote>
        <paragraph>
            Block quote
    <paragraph classes="three">
        Paragraph
"""],
["""\
.. class:: four

Section Title
=============

Paragraph
""",
"""\
<document source="test data">
    <section classes="four" ids="section-title" names="section\ title">
        <title>
            Section Title
        <paragraph>
            Paragraph
"""],
["""\
.. class:: multiple

   paragraph 1

   paragraph 2
""",
"""\
<document source="test data">
    <paragraph classes="multiple">
        paragraph 1
    <paragraph classes="multiple">
        paragraph 2
"""],
["""\
.. class:: multiple

   .. Just a comment.  It's silly, but possible
""",
"""\
<document source="test data">
    <comment classes="multiple" xml:space="preserve">
        Just a comment.  It's silly, but possible
"""],
["""\
.. class::

.. class:: 99
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Error in "class" directive:
            1 argument(s) required, 0 supplied.
        <literal_block xml:space="preserve">
            .. class::
    <system_message level="3" line="3" source="test data" type="ERROR">
        <paragraph>
            Invalid class attribute value for "class" directive: "99".
        <literal_block xml:space="preserve">
            .. class:: 99
"""],
["""\
.. class:: one
.. class:: two

multiple class values may be assigned to one element
""",
"""\
<document source="test data">
    <paragraph classes="one two">
        multiple class values may be assigned to one element
"""],
["""\
.. class:: one two

multiple class values may be assigned to one element
""",
"""\
<document source="test data">
    <paragraph classes="one two">
        multiple class values may be assigned to one element
"""],
["""\
.. class:: fancy

2. List starts at 2.
3. Class should apply to list, not to system message.
""",
"""\
<document source="test data">
    <enumerated_list classes="fancy" enumtype="arabic" prefix="" start="2" suffix=".">
        <list_item>
            <paragraph>
                List starts at 2.
        <list_item>
            <paragraph>
                Class should apply to list, not to system message.
    <system_message level="1" line="3" source="test data" type="INFO">
        <paragraph>
            Enumerated list start value not ordinal-1: "2" (ordinal 2)
"""],
["""\
2. List starts at 2.
3. Class should apply to next paragraph, not to system message.

   .. class:: fancy

A paragraph.
""",
"""\
<document source="test data">
    <enumerated_list enumtype="arabic" prefix="" start="2" suffix=".">
        <list_item>
            <paragraph>
                List starts at 2.
        <list_item>
            <paragraph>
                Class should apply to next paragraph, not to system message.
    <system_message level="1" line="1" source="test data" type="INFO">
        <paragraph>
            Enumerated list start value not ordinal-1: "2" (ordinal 2)
    <paragraph classes="fancy">
        A paragraph.
"""],
])


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
