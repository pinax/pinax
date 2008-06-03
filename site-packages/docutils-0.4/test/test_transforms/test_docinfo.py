#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 4173 $
# Date: $Date: 2005-12-11 22:57:53 +0100 (Sun, 11 Dec 2005) $
# Copyright: This module has been placed in the public domain.

"""
Tests for docutils.transforms.frontmatter.DocInfo.
"""

from __init__ import DocutilsTestSupport
from docutils.transforms.frontmatter import DocInfo
from docutils.parsers.rst import Parser


def suite():
    parser = Parser()
    s = DocutilsTestSupport.TransformTestSuite(parser)
    s.generateTests(totest)
    return s

totest = {}

totest['bibliographic_field_lists'] = ((DocInfo,), [
["""\
.. Bibliographic element extraction.

:Abstract:
    There can only be one abstract.

    It is automatically moved to the end of the other bibliographic elements.

:Author: Me
:Version: 1
:Date: 2001-08-11
:Parameter i: integer
""",
"""\
<document source="test data">
    <docinfo>
        <author>
            Me
        <version>
            1
        <date>
            2001-08-11
        <field>
            <field_name>
                Parameter i
            <field_body>
                <paragraph>
                    integer
    <topic classes="abstract">
        <title>
            Abstract
        <paragraph>
            There can only be one abstract.
        <paragraph>
            It is automatically moved to the end of the other bibliographic elements.
    <comment xml:space="preserve">
        Bibliographic element extraction.
"""],
["""\
.. Bibliographic element extraction.

:Abstract: Abstract 1.
:Author: Me
:Address: 123 My Street
          Example, EX
:Contact: me@my.org
:Version: 1
:Abstract: Abstract 2 (should generate a warning).
:Date: 2001-08-11
:Parameter i: integer
""",
"""\
<document source="test data">
    <docinfo>
        <author>
            Me
        <address xml:space="preserve">
            123 My Street
            Example, EX
        <contact>
            <reference refuri="mailto:me@my.org">
                me@my.org
        <version>
            1
        <field>
            <field_name>
                Abstract
            <field_body>
                <paragraph>
                    Abstract 2 (should generate a warning).
                <system_message level="2" line="9" source="test data" type="WARNING">
                    <paragraph>
                        There can only be one "Abstract" field.
        <date>
            2001-08-11
        <field>
            <field_name>
                Parameter i
            <field_body>
                <paragraph>
                    integer
    <topic classes="abstract">
        <title>
            Abstract
        <paragraph>
            Abstract 1.
    <comment xml:space="preserve">
        Bibliographic element extraction.
"""],
["""\
:Author: - must be a paragraph
:Status: a *simple* paragraph
:Date: But only one

       paragraph.
:Version:

.. and not empty either
""",
"""\
<document source="test data">
    <docinfo>
        <field>
            <field_name>
                Author
            <field_body>
                <bullet_list bullet="-">
                    <list_item>
                        <paragraph>
                            must be a paragraph
                <system_message level="2" line="1" source="test data" type="WARNING">
                    <paragraph>
                        Cannot extract bibliographic field "Author" containing anything other than a single paragraph.
        <status>
            a \n\
            <emphasis>
                simple
             paragraph
        <field>
            <field_name>
                Date
            <field_body>
                <paragraph>
                    But only one
                <paragraph>
                    paragraph.
                <system_message level="2" line="3" source="test data" type="WARNING">
                    <paragraph>
                        Cannot extract compound bibliographic field "Date".
        <field>
            <field_name>
                Version
            <field_body>
                <system_message level="2" line="6" source="test data" type="WARNING">
                    <paragraph>
                        Cannot extract empty bibliographic field "Version".
    <comment xml:space="preserve">
        and not empty either
"""],
["""\
:Authors: Me, Myself, **I**
:Authors: PacMan; Ms. PacMan; PacMan, Jr.
:Authors:
    Here

    There

    *Everywhere*
:Authors: - First
          - Second
          - Third
""",
"""\
<document source="test data">
    <docinfo>
        <authors>
            <author>
                Me
            <author>
                Myself
            <author>
                I
        <authors>
            <author>
                PacMan
            <author>
                Ms. PacMan
            <author>
                PacMan, Jr.
        <authors>
            <author>
                Here
            <author>
                There
            <author>
                <emphasis>
                    Everywhere
        <authors>
            <author>
                First
            <author>
                Second
            <author>
                Third
"""],
["""\
:Authors: Only One
:Authors: One, Only;
""",
"""\
<document source="test data">
    <docinfo>
        <authors>
            <author>
                Only One
        <authors>
            <author>
                One, Only
"""],
["""\
:Authors:

:Authors: 1. One
          2. Two

:Authors:
    -
    -

:Authors:
    - One

    Two

:Authors:
    - One

      Two
""",
"""\
<document source="test data">
    <docinfo>
        <field>
            <field_name>
                Authors
            <field_body>
                <system_message level="2" line="1" source="test data" type="WARNING">
                    <paragraph>
                        Cannot extract empty bibliographic field "Authors".
        <field>
            <field_name>
                Authors
            <field_body>
                <enumerated_list enumtype="arabic" prefix="" suffix=".">
                    <list_item>
                        <paragraph>
                            One
                    <list_item>
                        <paragraph>
                            Two
                <system_message level="2" line="3" source="test data" type="WARNING">
                    <paragraph>
                        Bibliographic field "Authors" incompatible with extraction: it must contain either a single paragraph (with authors separated by one of ";,"), multiple paragraphs (one per author), or a bullet list with one paragraph (one author) per item.
        <field>
            <field_name>
                Authors
            <field_body>
                <bullet_list bullet="-">
                    <list_item>
                    <list_item>
                <system_message level="2" line="6" source="test data" type="WARNING">
                    <paragraph>
                        Bibliographic field "Authors" incompatible with extraction: it must contain either a single paragraph (with authors separated by one of ";,"), multiple paragraphs (one per author), or a bullet list with one paragraph (one author) per item.
        <field>
            <field_name>
                Authors
            <field_body>
                <bullet_list bullet="-">
                    <list_item>
                        <paragraph>
                            One
                <paragraph>
                    Two
                <system_message level="2" line="10" source="test data" type="WARNING">
                    <paragraph>
                        Bibliographic field "Authors" incompatible with extraction: it must contain either a single paragraph (with authors separated by one of ";,"), multiple paragraphs (one per author), or a bullet list with one paragraph (one author) per item.
        <field>
            <field_name>
                Authors
            <field_body>
                <bullet_list bullet="-">
                    <list_item>
                        <paragraph>
                            One
                        <paragraph>
                            Two
                <system_message level="2" line="15" source="test data" type="WARNING">
                    <paragraph>
                        Bibliographic field "Authors" incompatible with extraction: it must contain either a single paragraph (with authors separated by one of ";,"), multiple paragraphs (one per author), or a bullet list with one paragraph (one author) per item.
"""],
["""\
.. RCS keyword extraction.

:Status: (some text) $""" + """RCSfile: test_docinfo.py,v $ (more text) 
:Date: (some text) $""" + """Date: 2002/10/08 01:34:23 $ (more text)
:Date: (some text) $""" + """Date: 2005-03-26T16:21:28.693201Z $ (more text)
:Version: (some text) $""" + """Revision: 1.1 $ (more text)
""",
"""\
<document source="test data">
    <docinfo>
        <status>
            (some text) test_docinfo.py (more text)
        <date>
            (some text) 2002-10-08 (more text)
        <date>
            (some text) 2005-03-26 (more text)
        <version>
            (some text) 1.1 (more text)
    <comment xml:space="preserve">
        RCS keyword extraction.
"""],
])


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
