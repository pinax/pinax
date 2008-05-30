#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 3915 $
# Date: $Date: 2005-10-02 03:06:42 +0200 (Sun, 02 Oct 2005) $
# Copyright: This module has been placed in the public domain.

"""
Tests for `docutils.transforms.parts.Contents` (via
`docutils.transforms.universal.LastReaderPending`).
"""

from __init__ import DocutilsTestSupport
from docutils.transforms.references import Substitutions
from docutils.parsers.rst import Parser


def suite():
    parser = Parser()
    s = DocutilsTestSupport.TransformTestSuite(parser)
    s.generateTests(totest)
    return s

totest = {}

totest['tables_of_contents'] = ((Substitutions,), [
["""\
.. contents::

Title 1
=======
Paragraph 1.

Title_ 2
--------
Paragraph 2.

_`Title` 3
``````````
Paragraph 3.

Title 4
-------
Paragraph 4.
""",
"""\
<document source="test data">
    <topic classes="contents" ids="contents" names="contents">
        <title>
            Contents
        <bullet_list>
            <list_item>
                <paragraph>
                    <reference ids="id1" refid="title-1">
                        Title 1
                <bullet_list>
                    <list_item>
                        <paragraph>
                            <reference ids="id2" refid="title-2">
                                Title
                                 2
                        <bullet_list>
                            <list_item>
                                <paragraph>
                                    <reference ids="id3" refid="title-3">
                                        Title
                                         3
                    <list_item>
                        <paragraph>
                            <reference ids="id4" refid="title-4">
                                Title 4
    <section ids="title-1" names="title\ 1">
        <title refid="id1">
            Title 1
        <paragraph>
            Paragraph 1.
        <section ids="title-2" names="title\ 2">
            <title>
                <reference name="Title" refname="title">
                    Title
                 2
            <paragraph>
                Paragraph 2.
            <section ids="title-3" names="title\ 3">
                <title refid="id3">
                    <target ids="title" names="title">
                        Title
                     3
                <paragraph>
                    Paragraph 3.
        <section ids="title-4" names="title\ 4">
            <title refid="id4">
                Title 4
            <paragraph>
                Paragraph 4.
"""],
["""\
.. contents:: Table of Contents

Title 1
=======
Paragraph 1.

Title 2
-------
Paragraph 2.
""",
"""\
<document source="test data">
    <topic classes="contents" ids="table-of-contents" names="table\ of\ contents">
        <title>
            Table of Contents
        <bullet_list>
            <list_item>
                <paragraph>
                    <reference ids="id1" refid="title-1">
                        Title 1
                <bullet_list>
                    <list_item>
                        <paragraph>
                            <reference ids="id2" refid="title-2">
                                Title 2
    <section ids="title-1" names="title\ 1">
        <title refid="id1">
            Title 1
        <paragraph>
            Paragraph 1.
        <section ids="title-2" names="title\ 2">
            <title refid="id2">
                Title 2
            <paragraph>
                Paragraph 2.
"""],
["""\
.. contents:: There's an image in Title 2

Title 1
=======
Paragraph 1.

|Title 2|
=========
Paragraph 2.

.. |Title 2| image:: title2.png
""",
"""\
<document source="test data">
    <topic classes="contents" ids="there-s-an-image-in-title-2" names="there's\ an\ image\ in\ title\ 2">
        <title>
            There's an image in Title 2
        <bullet_list>
            <list_item>
                <paragraph>
                    <reference ids="id1" refid="title-1">
                        Title 1
            <list_item>
                <paragraph>
                    <reference ids="id2" refid="title-2">
                        Title 2
    <section ids="title-1" names="title\ 1">
        <title refid="id1">
            Title 1
        <paragraph>
            Paragraph 1.
    <section ids="title-2" names="title\ 2">
        <title refid="id2">
            <image alt="Title 2" uri="title2.png">
        <paragraph>
            Paragraph 2.
        <substitution_definition names="Title\ 2">
            <image alt="Title 2" uri="title2.png">
"""],                                   # emacs cruft: "
["""\
.. contents::
   :depth: 2

Title 1
=======
Paragraph 1.

Title 2
-------
Paragraph 2.

Title 3
```````
Paragraph 3.

Title 4
-------
Paragraph 4.
""",
"""\
<document source="test data">
    <topic classes="contents" ids="contents" names="contents">
        <title>
            Contents
        <bullet_list>
            <list_item>
                <paragraph>
                    <reference ids="id1" refid="title-1">
                        Title 1
                <bullet_list>
                    <list_item>
                        <paragraph>
                            <reference ids="id2" refid="title-2">
                                Title 2
                    <list_item>
                        <paragraph>
                            <reference ids="id3" refid="title-4">
                                Title 4
    <section ids="title-1" names="title\ 1">
        <title refid="id1">
            Title 1
        <paragraph>
            Paragraph 1.
        <section ids="title-2" names="title\ 2">
            <title refid="id2">
                Title 2
            <paragraph>
                Paragraph 2.
            <section ids="title-3" names="title\ 3">
                <title>
                    Title 3
                <paragraph>
                    Paragraph 3.
        <section ids="title-4" names="title\ 4">
            <title refid="id3">
                Title 4
            <paragraph>
                Paragraph 4.
"""],
["""\
Title 1
=======

.. contents::
   :local:

Paragraph 1.

Title 2
-------
Paragraph 2.

Title 3
```````
Paragraph 3.

Title 4
-------
Paragraph 4.
""",
"""\
<document source="test data">
    <section ids="title-1" names="title\ 1">
        <title>
            Title 1
        <topic classes="contents local" ids="contents" names="contents">
            <bullet_list>
                <list_item>
                    <paragraph>
                        <reference ids="id1" refid="title-2">
                            Title 2
                    <bullet_list>
                        <list_item>
                            <paragraph>
                                <reference ids="id2" refid="title-3">
                                    Title 3
                <list_item>
                    <paragraph>
                        <reference ids="id3" refid="title-4">
                            Title 4
        <paragraph>
            Paragraph 1.
        <section ids="title-2" names="title\ 2">
            <title refid="id1">
                Title 2
            <paragraph>
                Paragraph 2.
            <section ids="title-3" names="title\ 3">
                <title refid="id2">
                    Title 3
                <paragraph>
                    Paragraph 3.
        <section ids="title-4" names="title\ 4">
            <title refid="id3">
                Title 4
            <paragraph>
                Paragraph 4.
"""],
["""\
.. contents::
   :local:

Test duplicate name "Contents".

Section
--------
Paragraph.
""",
"""\
<document source="test data">
    <topic classes="contents local" ids="contents" names="contents">
        <bullet_list>
            <list_item>
                <paragraph>
                    <reference ids="id1" refid="section">
                        Section
    <paragraph>
        Test duplicate name "Contents".
    <section ids="section" names="section">
        <title refid="id1">
            Section
        <paragraph>
            Paragraph.
"""],
["""\
.. contents::
   :backlinks: top

Section
--------
Paragraph.
""",
"""\
<document source="test data">
    <topic classes="contents" ids="contents" names="contents">
        <title>
            Contents
        <bullet_list>
            <list_item>
                <paragraph>
                    <reference ids="id1" refid="section">
                        Section
    <section ids="section" names="section">
        <title refid="contents">
            Section
        <paragraph>
            Paragraph.
"""],
["""\
.. contents::
   :backlinks: none

Section
--------
Paragraph.
""",
"""\
<document source="test data">
    <topic classes="contents" ids="contents" names="contents">
        <title>
            Contents
        <bullet_list>
            <list_item>
                <paragraph>
                    <reference ids="id1" refid="section">
                        Section
    <section ids="section" names="section">
        <title>
            Section
        <paragraph>
            Paragraph.
"""],
["""\
.. contents::

Degenerate case, no table of contents generated.
""",
"""\
<document source="test data">
    <paragraph>
        Degenerate case, no table of contents generated.
"""],
["""\
Title 1
=======

Paragraph 1.

.. sidebar:: Contents

   .. contents::
      :local:

Title 2
-------
Paragraph 2.

Title 3
```````
Paragraph 3.
""",
"""\
<document source="test data">
    <section ids="title-1" names="title\ 1">
        <title>
            Title 1
        <paragraph>
            Paragraph 1.
        <sidebar>
            <title>
                Contents
            <topic classes="contents local" ids="contents" names="contents">
                <bullet_list>
                    <list_item>
                        <paragraph>
                            <reference ids="id1" refid="title-2">
                                Title 2
                        <bullet_list>
                            <list_item>
                                <paragraph>
                                    <reference ids="id2" refid="title-3">
                                        Title 3
        <section ids="title-2" names="title\ 2">
            <title refid="id1">
                Title 2
            <paragraph>
                Paragraph 2.
            <section ids="title-3" names="title\ 3">
                <title refid="id2">
                    Title 3
                <paragraph>
                    Paragraph 3.
"""],
])


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
