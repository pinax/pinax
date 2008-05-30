#! /usr/bin/env python

# Author: David Goodger, Dmitry Jemerov
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 3915 $
# Date: $Date: 2005-10-02 03:06:42 +0200 (Sun, 02 Oct 2005) $
# Copyright: This module has been placed in the public domain.

"""
Tests for `docutils.transforms.parts.SectNum` (via
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

totest['section_numbers'] = ((Substitutions,), [
["""\
.. sectnum::

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
u"""\
<document source="test data">
    <section ids="title-1" names="title\ 1">
        <title auto="1">
            <generated classes="sectnum">
                1\u00a0\u00a0\u00a0
            Title 1
        <paragraph>
            Paragraph 1.
        <section ids="title-2" names="title\ 2">
            <title auto="1">
                <generated classes="sectnum">
                    1.1\u00a0\u00a0\u00a0
                Title 2
            <paragraph>
                Paragraph 2.
            <section ids="title-3" names="title\ 3">
                <title auto="1">
                    <generated classes="sectnum">
                        1.1.1\u00a0\u00a0\u00a0
                    Title 3
                <paragraph>
                    Paragraph 3.
        <section ids="title-4" names="title\ 4">
            <title auto="1">
                <generated classes="sectnum">
                    1.2\u00a0\u00a0\u00a0
                Title 4
            <paragraph>
                Paragraph 4.
"""],
["""\
.. sectnum::

**Bold Title**
==============
Paragraph 1.
""",
u"""\
<document source="test data">
    <section ids="bold-title" names="bold\ title">
        <title auto="1">
            <generated classes="sectnum">
                1\u00a0\u00a0\u00a0
            <strong>
                Bold Title
        <paragraph>
            Paragraph 1.
"""],
["""\
.. sectnum:: :depth: 2

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
u"""\
<document source="test data">
    <section ids="title-1" names="title\ 1">
        <title auto="1">
            <generated classes="sectnum">
                1\u00a0\u00a0\u00a0
            Title 1
        <paragraph>
            Paragraph 1.
        <section ids="title-2" names="title\ 2">
            <title auto="1">
                <generated classes="sectnum">
                    1.1\u00a0\u00a0\u00a0
                Title 2
            <paragraph>
                Paragraph 2.
            <section ids="title-3" names="title\ 3">
                <title>
                    Title 3
                <paragraph>
                    Paragraph 3.
        <section ids="title-4" names="title\ 4">
            <title auto="1">
                <generated classes="sectnum">
                    1.2\u00a0\u00a0\u00a0
                Title 4
            <paragraph>
                Paragraph 4.
"""],
["""\
.. contents::
.. sectnum:: :depth: 2

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
u"""\
<document source="test data">
    <topic classes="contents" ids="contents" names="contents">
        <title>
            Contents
        <bullet_list classes="auto-toc">
            <list_item>
                <paragraph>
                    <reference ids="id1" refid="title-1">
                        <generated classes="sectnum">
                            1\u00a0\u00a0\u00a0
                        Title 1
                <bullet_list classes="auto-toc">
                    <list_item>
                        <paragraph>
                            <reference ids="id2" refid="title-2">
                                <generated classes="sectnum">
                                    1.1\u00a0\u00a0\u00a0
                                Title 2
                        <bullet_list>
                            <list_item>
                                <paragraph>
                                    <reference ids="id3" refid="title-3">
                                        Title 3
                    <list_item>
                        <paragraph>
                            <reference ids="id4" refid="title-4">
                                <generated classes="sectnum">
                                    1.2\u00a0\u00a0\u00a0
                                Title 4
    <section ids="title-1" names="title\ 1">
        <title auto="1" refid="id1">
            <generated classes="sectnum">
                1\u00a0\u00a0\u00a0
            Title 1
        <paragraph>
            Paragraph 1.
        <section ids="title-2" names="title\ 2">
            <title auto="1" refid="id2">
                <generated classes="sectnum">
                    1.1\u00a0\u00a0\u00a0
                Title 2
            <paragraph>
                Paragraph 2.
            <section ids="title-3" names="title\ 3">
                <title refid="id3">
                    Title 3
                <paragraph>
                    Paragraph 3.
        <section ids="title-4" names="title\ 4">
            <title auto="1" refid="id4">
                <generated classes="sectnum">
                    1.2\u00a0\u00a0\u00a0
                Title 4
            <paragraph>
                Paragraph 4.
"""],
["""\
.. sectnum::
   :prefix: Arbitrary-

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
u"""\
<document source="test data">
    <section ids="title-1" names="title\ 1">
        <title auto="1">
            <generated classes="sectnum">
                Arbitrary-1\u00a0\u00a0\u00a0
            Title 1
        <paragraph>
            Paragraph 1.
        <section ids="title-2" names="title\ 2">
            <title auto="1">
                <generated classes="sectnum">
                    Arbitrary-1.1\u00a0\u00a0\u00a0
                Title 2
            <paragraph>
                Paragraph 2.
            <section ids="title-3" names="title\ 3">
                <title auto="1">
                    <generated classes="sectnum">
                        Arbitrary-1.1.1\u00a0\u00a0\u00a0
                    Title 3
                <paragraph>
                    Paragraph 3.
        <section ids="title-4" names="title\ 4">
            <title auto="1">
                <generated classes="sectnum">
                    Arbitrary-1.2\u00a0\u00a0\u00a0
                Title 4
            <paragraph>
                Paragraph 4.
"""],
["""\
.. sectnum::
   :start: 3
   
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
u"""\
<document source="test data">
    <section ids="title-1" names="title\ 1">
        <title auto="1">
            <generated classes="sectnum">
                3\u00a0\u00a0\u00a0
            Title 1
        <paragraph>
            Paragraph 1.
        <section ids="title-2" names="title\ 2">
            <title auto="1">
                <generated classes="sectnum">
                    3.1\u00a0\u00a0\u00a0
                Title 2
            <paragraph>
                Paragraph 2.
            <section ids="title-3" names="title\ 3">
                <title auto="1">
                    <generated classes="sectnum">
                        3.1.1\u00a0\u00a0\u00a0
                    Title 3
                <paragraph>
                    Paragraph 3.
        <section ids="title-4" names="title\ 4">
            <title auto="1">
                <generated classes="sectnum">
                    3.2\u00a0\u00a0\u00a0
                Title 4
            <paragraph>
                Paragraph 4.
"""],
["""\
.. sectnum::
   :prefix: (5.9.
   :suffix: )
   :start: 3
   
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
u"""\
<document source="test data">
    <section ids="title-1" names="title\ 1">
        <title auto="1">
            <generated classes="sectnum">
                (5.9.3)\u00a0\u00a0\u00a0
            Title 1
        <paragraph>
            Paragraph 1.
        <section ids="title-2" names="title\ 2">
            <title auto="1">
                <generated classes="sectnum">
                    (5.9.3.1)\u00a0\u00a0\u00a0
                Title 2
            <paragraph>
                Paragraph 2.
            <section ids="title-3" names="title\ 3">
                <title auto="1">
                    <generated classes="sectnum">
                        (5.9.3.1.1)\u00a0\u00a0\u00a0
                    Title 3
                <paragraph>
                    Paragraph 3.
        <section ids="title-4" names="title\ 4">
            <title auto="1">
                <generated classes="sectnum">
                    (5.9.3.2)\u00a0\u00a0\u00a0
                Title 4
            <paragraph>
                Paragraph 4.
"""],
])


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
