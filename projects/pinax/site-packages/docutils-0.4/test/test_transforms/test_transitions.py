#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 4132 $
# Date: $Date: 2005-12-03 03:13:12 +0100 (Sat, 03 Dec 2005) $
# Copyright: This module has been placed in the public domain.

"""
Test module for misc.Transitions transform.
"""

from __init__ import DocutilsTestSupport # must be imported before docutils
from docutils.transforms.misc import Transitions
from docutils.parsers.rst import Parser

def suite():
    parser = Parser()
    s = DocutilsTestSupport.TransformTestSuite(parser)
    s.generateTests(totest)
    return s


totest = {}

totest['transitions'] = ((Transitions,), [
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
A paragraph.

----------

Section 1
=========

Paragraph.
""",
"""\
<document source="test data">
    <paragraph>
        A paragraph.
    <transition>
    <section ids="section-1" names="section\ 1">
        <title>
            Section 1
        <paragraph>
            Paragraph.
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
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Document or section may not begin with a transition.
    <transition>
    <paragraph>
        A section or document may not begin with a transition.
    <paragraph>
        The DTD specifies that two transitions may not
        be adjacent:
    <transition>
    <system_message level="3" line="10" source="test data" type="ERROR">
        <paragraph>
            At least one body element must separate transitions; adjacent transitions are not allowed.
    <transition>
    <system_message level="3" line="12" source="test data" type="ERROR">
        <paragraph>
            At least one body element must separate transitions; adjacent transitions are not allowed.
    <transition>
    <paragraph>
        The DTD also specifies that a section or document
        may not end with a transition.
    <transition>
    <system_message level="3" line="17" source="test data" type="ERROR">
        <paragraph>
            Document may not end with a transition.
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
        <system_message level="3" line="6" source="test data" type="ERROR">
            <paragraph>
                Document or section may not begin with a transition.
        <transition>
        <paragraph>
            The next transition is legal:
    <transition>
    <section ids="section-2" names="section\ 2">
        <title>
            Section 2
        <system_message level="3" line="15" source="test data" type="ERROR">
            <paragraph>
                Document or section may not begin with a transition.
        <transition>
        <system_message level="3" line="15" source="test data" type="ERROR">
            <paragraph>
                Document may not end with a transition.
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
    <system_message level="3" line="5" source="test data" type="ERROR">
        <paragraph>
            At least one body element must separate transitions; adjacent transitions are not allowed.
    <transition>
    <system_message level="3" line="5" source="test data" type="ERROR">
        <paragraph>
            Document may not end with a transition.
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
    <system_message level="3" line="5" source="test data" type="ERROR">
        <paragraph>
            At least one body element must separate transitions; adjacent transitions are not allowed.
    <transition>
    <system_message level="3" line="5" source="test data" type="ERROR">
        <paragraph>
            Document may not end with a transition.
"""],
["""\
----------

Document beginning with a transition.
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Document or section may not begin with a transition.
    <transition>
    <paragraph>
        Document beginning with a transition.
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
        <system_message level="3" line="4" source="test data" type="ERROR">
            <paragraph>
                Document or section may not begin with a transition.
        <transition>
        <system_message level="3" line="6" source="test data" type="ERROR">
            <paragraph>
                At least one body element must separate transitions; adjacent transitions are not allowed.
        <transition>
        <system_message level="3" line="8" source="test data" type="ERROR">
            <paragraph>
                At least one body element must separate transitions; adjacent transitions are not allowed.
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
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Document or section may not begin with a transition.
    <transition>
    <system_message level="3" line="3" source="test data" type="ERROR">
        <paragraph>
            At least one body element must separate transitions; adjacent transitions are not allowed.
    <transition>
    <system_message level="3" line="5" source="test data" type="ERROR">
        <paragraph>
            At least one body element must separate transitions; adjacent transitions are not allowed.
    <transition>
    <system_message level="3" line="5" source="test data" type="ERROR">
        <paragraph>
            Document may not end with a transition.
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
    <system_message level="3" line="3" source="test data" type="ERROR">
        <paragraph>
            Document may not end with a transition.
"""],
])


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
