#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 4212 $
# Date: $Date: 2005-12-14 15:51:34 +0100 (Wed, 14 Dec 2005) $
# Copyright: This module has been placed in the public domain.

"""
Tests for misc.py "include" directive.
"""

import os.path
import sys
from __init__ import DocutilsTestSupport
from docutils.parsers.rst import states


def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

mydir = 'test_parsers/test_rst/test_directives/'
include1 = os.path.join(mydir, 'include1.txt')
include1rel = DocutilsTestSupport.utils.relative_path(None, include1)
include2 = os.path.join(mydir, 'include2.txt')
include3 = os.path.join(mydir, 'include3.txt')
include8 = os.path.join(mydir, 'include8.txt')
include10 = os.path.join(mydir, 'include10.txt')
include10rel = DocutilsTestSupport.utils.relative_path(None, include10)
include11 = os.path.join(mydir, 'include 11.txt')
include11rel = DocutilsTestSupport.utils.relative_path(None, include11)
utf_16_file = os.path.join(mydir, 'utf-16.csv')
utf_16_file_rel = DocutilsTestSupport.utils.relative_path(None, utf_16_file)
nonexistent = os.path.join(os.path.dirname(states.__file__),
                           'include', 'nonexistent')
nonexistent_rel = DocutilsTestSupport.utils.relative_path(
    os.path.join(DocutilsTestSupport.testroot, 'dummy'), nonexistent)

totest = {}

totest['include'] = [
["""\
Include Test
============

.. include:: %s

A paragraph.
""" % include1,
"""\
<document source="test data">
    <section ids="include-test" names="include\ test">
        <title>
            Include Test
        <section ids="inclusion-1" names="inclusion\ 1">
            <title>
                Inclusion 1
            <paragraph>
                This file is used by \n\
                <literal>
                    test_include.py
                .
            <paragraph>
                A paragraph.
"""],
["""\
Include Test
============

.. include:: %s
   :literal:

A paragraph.
""" % include1,
"""\
<document source="test data">
    <section ids="include-test" names="include\ test">
        <title>
            Include Test
        <literal_block source="%s" xml:space="preserve">
            Inclusion 1
            -----------
            \n\
            This file is used by ``test_include.py``.
        <paragraph>
            A paragraph.
""" % include1rel],
["""\
Let's test the parse context.

    This paragraph is in a block quote.

    .. include:: %s

The included paragraphs should also be in the block quote.
""" % include2,
"""\
<document source="test data">
    <paragraph>
        Let's test the parse context.
    <block_quote>
        <paragraph>
            This paragraph is in a block quote.
        <paragraph>
            Here are some paragraphs
            that can appear at any level.
        <paragraph>
            This file (include2.txt) is used by
            <literal>
                test_include.py
            .
    <paragraph>
        The included paragraphs should also be in the block quote.
"""],
["""\
Include Test
============

.. include:: nonexistent.txt

A paragraph.
""",
"""\
<document source="test data">
    <section ids="include-test" names="include\ test">
        <title>
            Include Test
        <system_message level="4" line="4" source="test data" type="SEVERE">
            <paragraph>
                Problems with "include" directive path:
                IOError: [Errno 2] No such file or directory: 'nonexistent.txt'.
            <literal_block xml:space="preserve">
                .. include:: nonexistent.txt
        <paragraph>
            A paragraph.
"""],
["""\
Include Test
============

.. include:: %s

.. include:: %s

A paragraph.
""" % (include1, include1),
"""\
<document source="test data">
    <section ids="include-test" names="include\ test">
        <title>
            Include Test
        <section dupnames="inclusion\ 1" ids="inclusion-1">
            <title>
                Inclusion 1
            <paragraph>
                This file is used by 
                <literal>
                    test_include.py
                .
        <section dupnames="inclusion\ 1" ids="id1">
            <title>
                Inclusion 1
            <system_message backrefs="id1" level="1" line="2" source="%s" type="INFO">
                <paragraph>
                    Duplicate implicit target name: "inclusion 1".
            <paragraph>
                This file is used by 
                <literal>
                    test_include.py
                .
            <paragraph>
                A paragraph.
""" % include1rel],
["""\
Include Test
============

.. include:: %s

----------

.. include:: %s

A paragraph.
""" % (include1, include1),
"""\
<document source="test data">
    <section ids="include-test" names="include\ test">
        <title>
            Include Test
        <section dupnames="inclusion\ 1" ids="inclusion-1">
            <title>
                Inclusion 1
            <paragraph>
                This file is used by \n\
                <literal>
                    test_include.py
                .
            <transition>
        <section dupnames="inclusion\ 1" ids="id1">
            <title>
                Inclusion 1
            <system_message backrefs="id1" level="1" line="2" source="%s" type="INFO">
                <paragraph>
                    Duplicate implicit target name: "inclusion 1".
            <paragraph>
                This file is used by \n\
                <literal>
                    test_include.py
                .
            <paragraph>
                A paragraph.
""" % include1rel],
["""\
In test data

.. include:: %s
""" % include3,
"""\
<document source="test data">
    <paragraph>
        In test data
    <paragraph>
        In include3.txt
    <paragraph>
        In includes/include4.txt
    <paragraph>
        In includes/include5.txt
    <paragraph>
        In includes/more/include6.txt
    <paragraph>
        In includes/sibling/include7.txt
"""],
["""\
In test data

Section
=======

(Section contents in nested parse; slice of input_lines ViewList.)

.. include:: %s
""" % include3,
"""\
<document source="test data">
    <paragraph>
        In test data
    <section ids="section" names="section">
        <title>
            Section
        <paragraph>
            (Section contents in nested parse; slice of input_lines ViewList.)
        <paragraph>
            In include3.txt
        <paragraph>
            In includes/include4.txt
        <paragraph>
            In includes/include5.txt
        <paragraph>
            In includes/more/include6.txt
        <paragraph>
            In includes/sibling/include7.txt
"""],
["""\
Testing relative includes:

.. include:: %s
""" % include8,
"""\
<document source="test data">
    <paragraph>
        Testing relative includes:
    <paragraph>
        In include8.txt
    <paragraph>
        In ../includes/include9.txt.
    <paragraph>
        Here are some paragraphs
        that can appear at any level.
    <paragraph>
        This file (include2.txt) is used by
        <literal>
            test_include.py
        .
"""],
["""\
Encoding:

.. include:: %s
   :encoding: utf-16
""" % utf_16_file_rel,
u"""\
<document source="test data">
    <paragraph>
        Encoding:
    <paragraph>
        "Treat", "Quantity", "Description"
        "Albatr\xb0\xdf", 2.99, "\xa1On a \\u03c3\\u03c4\\u03b9\\u03ba!"
        "Crunchy Frog", 1.49, "If we took the b\xf6nes out, it wouldn\\u2019t be
        crunchy, now would it?"
        "Gannet Ripple", 1.99, "\xbfOn a \\u03c3\\u03c4\\u03b9\\u03ba?"
"""],
["""\
Include file is UTF-16-encoded, and is not valid ASCII.

.. include:: %s
   :encoding: ascii
""" % utf_16_file_rel,
"""\
<document source="test data">
    <paragraph>
        Include file is UTF-16-encoded, and is not valid ASCII.
    <system_message level="4" line="3" source="test data" type="SEVERE">
        <paragraph>
            Problem with "include" directive:
            UnicodeError: Unable to decode input data.  Tried the following encodings: 'ascii'.
            (UnicodeDecodeError: 'ascii' codec can't decode byte 0xfe in position 0: ordinal not in range(128))
        <literal_block xml:space="preserve">
            .. include:: %s
               :encoding: ascii
""" % utf_16_file_rel],
# @@@ BUG with errors reported with incorrect "source" & "line":
# ["""\
# Testing bad charent includes:
#
# .. include:: %s
# """ % include10,
# """\
# <document source="test data">
#     <paragraph>
#         Testing bad charent includes:
#     <system_message level="3" line="1" source="%s" type="ERROR">
#         <paragraph>
#             Invalid character code: 0xFFFFFFFFF
#             int() literal too large: FFFFFFFFF
#         <literal_block xml:space="preserve">
#             unicode:: 0xFFFFFFFFF
#     <system_message level="2" line="1" source="%s" type="WARNING">
#         <paragraph>
#             Substitution definition "bad" empty or invalid.
#         <literal_block xml:space="preserve">
#             .. |bad| unicode:: 0xFFFFFFFFF
# """ % (include10rel, include10rel)],
["""\
Include file with whitespace in the path:

.. include:: %s
""" % include11rel,
"""\
<document source="test data">
    <paragraph>
        Include file with whitespace in the path:
    <paragraph>
        some text
"""],
["""\
Standard include data file:

.. include:: <isogrk4.txt>
""",
"""\
<document source="test data">
    <paragraph>
        Standard include data file:
    <comment xml:space="preserve">
        This data file has been placed in the public domain.
    <comment xml:space="preserve">
        Derived from the Unicode character mappings available from
        <http://www.w3.org/2003/entities/xml/>.
        Processed by unicode2rstsubs.py, part of Docutils:
        <http://docutils.sourceforge.net>.
    <substitution_definition names="b.Gammad">
        \\u03dc
    <substitution_definition names="b.gammad">
        \\u03dd
"""],
["""\
Nonexistent standard include data file:

.. include:: <nonexistent>
""",
"""\
<document source="test data">
    <paragraph>
        Nonexistent standard include data file:
    <system_message level="4" line="3" source="test data" type="SEVERE">
        <paragraph>
            Problems with "include" directive path:
            IOError: [Errno 2] No such file or directory: '%s'.
        <literal_block xml:space="preserve">
            .. include:: <nonexistent>
""" % nonexistent_rel],
]


# Skip tests whose output contains "UnicodeDecodeError" if we are not
# using Python 2.3 or higher.
if sys.version_info < (2, 3):
    for i in range(len(totest['include'])):
        if totest['include'][i][1].find('UnicodeDecodeError') != -1:
            del totest['include'][i]
            print ("Test totest['include'][%s] skipped; "
                   "Python 2.3+ required for expected output." % i)
            # Assume we have only one of these tests.
            break


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
