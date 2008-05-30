#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 3915 $
# Date: $Date: 2005-10-02 03:06:42 +0200 (Sun, 02 Oct 2005) $
# Copyright: This module has been placed in the public domain.

"""
Tests for transition markers.
"""

from __init__ import DocutilsTestSupport

def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

totest = {}

# See DocutilsTestSupport.ParserTestSuite.generateTests for a
# description of the 'totest' data structure.
totest['transitions'] = [
["""\
Test transition markers.

--------

Paragraph
""",
"""\
<document source="test data">
    <paragraph>
        Test transition markers.
    <transition>
    <paragraph>
        Paragraph
"""],
["""\
Section 1
=========
First text division of section 1.

--------

Second text division of section 1.

Section 2
---------
Paragraph 2 in section 2.
""",
"""\
<document source="test data">
    <section ids="section-1" names="section\ 1">
        <title>
            Section 1
        <paragraph>
            First text division of section 1.
        <transition>
        <paragraph>
            Second text division of section 1.
        <section ids="section-2" names="section\ 2">
            <title>
                Section 2
            <paragraph>
                Paragraph 2 in section 2.
"""],
["""\
--------

A section or document may not begin with a transition.

The DTD specifies that two transitions may not
be adjacent:

--------

--------

--------

The DTD also specifies that a section or document
may not end with a transition.

--------
""",
"""\
<document source="test data">
    <transition>
    <paragraph>
        A section or document may not begin with a transition.
    <paragraph>
        The DTD specifies that two transitions may not
        be adjacent:
    <transition>
    <transition>
    <transition>
    <paragraph>
        The DTD also specifies that a section or document
        may not end with a transition.
    <transition>
"""],
["""\
Test unexpected transition markers.

    Block quote.

    --------

    Paragraph.
""",
"""\
<document source="test data">
    <paragraph>
        Test unexpected transition markers.
    <block_quote>
        <paragraph>
            Block quote.
        <system_message level="4" line="5" source="test data" type="SEVERE">
            <paragraph>
                Unexpected section title or transition.
            <literal_block xml:space="preserve">
                --------
        <paragraph>
            Paragraph.
"""],
["""\
Short transition marker.

---

Paragraph
""",
"""\
<document source="test data">
    <paragraph>
        Short transition marker.
    <paragraph>
        ---
    <paragraph>
        Paragraph
"""],
["""\
Sections with transitions at beginning and end.

Section 1
=========

----------

The next transition is legal:

----------

Section 2
=========

----------
""",
"""\
<document source="test data">
    <paragraph>
        Sections with transitions at beginning and end.
    <section ids="section-1" names="section\ 1">
        <title>
            Section 1
        <transition>
        <paragraph>
            The next transition is legal:
        <transition>
    <section ids="section-2" names="section\ 2">
        <title>
            Section 2
        <transition>
"""],
["""\
A paragraph, two transitions, and a blank line.

----------

----------

""",
"""\
<document source="test data">
    <paragraph>
        A paragraph, two transitions, and a blank line.
    <transition>
    <transition>
"""],
["""\
A paragraph and two transitions.

----------

----------
""", # the same:
"""\
<document source="test data">
    <paragraph>
        A paragraph and two transitions.
    <transition>
    <transition>
"""],
["""\
----------

Document beginning with a transition.
""",
"""\
<document source="test data">
    <transition>
    <paragraph>
        Document beginning with a transition.
"""],
["""\
Section 1
=========

Subsection 1
------------

Some text.

----------

Section 2
=========

Some text.
""",
"""\
<document source="test data">
    <section ids="section-1" names="section\ 1">
        <title>
            Section 1
        <section ids="subsection-1" names="subsection\ 1">
            <title>
                Subsection 1
            <paragraph>
                Some text.
            <transition>
    <section ids="section-2" names="section\ 2">
        <title>
            Section 2
        <paragraph>
            Some text.
"""],
["""\
Section 1
=========

----------

----------

----------

Section 2
=========

Some text.
""",
"""\
<document source="test data">
    <section ids="section-1" names="section\ 1">
        <title>
            Section 1
        <transition>
        <transition>
        <transition>
    <section ids="section-2" names="section\ 2">
        <title>
            Section 2
        <paragraph>
            Some text.
"""],
["""\
----------

----------

----------
""",
"""\
<document source="test data">
    <transition>
    <transition>
    <transition>
"""],
["""\
A paragraph.

----------

""",
"""\
<document source="test data">
    <paragraph>
        A paragraph.
    <transition>
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
