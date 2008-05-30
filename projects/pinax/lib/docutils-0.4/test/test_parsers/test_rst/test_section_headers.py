#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 3915 $
# Date: $Date: 2005-10-02 03:06:42 +0200 (Sun, 02 Oct 2005) $
# Copyright: This module has been placed in the public domain.

"""Tests for states.py."""

from __init__ import DocutilsTestSupport

def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

totest = {}

totest['section_headers'] = [
["""\
Title
=====

Paragraph.
""",
"""\
<document source="test data">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            Paragraph.
"""],
["""\
Title
=====
Paragraph (no blank line).
""",
"""\
<document source="test data">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            Paragraph (no blank line).
"""],
["""\
Paragraph.

Title
=====

Paragraph.
""",
"""\
<document source="test data">
    <paragraph>
        Paragraph.
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            Paragraph.
"""],
["""\
Test unexpected section titles.

    Title
    =====
    Paragraph.

    -----
    Title
    -----
    Paragraph.
""",
"""\
<document source="test data">
    <paragraph>
        Test unexpected section titles.
    <block_quote>
        <system_message level="4" line="4" source="test data" type="SEVERE">
            <paragraph>
                Unexpected section title.
            <literal_block xml:space="preserve">
                Title
                =====
        <paragraph>
            Paragraph.
        <system_message level="4" line="7" source="test data" type="SEVERE">
            <paragraph>
                Unexpected section title or transition.
            <literal_block xml:space="preserve">
                -----
        <system_message level="4" line="9" source="test data" type="SEVERE">
            <paragraph>
                Unexpected section title.
            <literal_block xml:space="preserve">
                Title
                -----
        <paragraph>
            Paragraph.
"""],
["""\
Title
====

Test short underline.
""",
"""\
<document source="test data">
    <section ids="title" names="title">
        <title>
            Title
        <system_message level="2" line="2" source="test data" type="WARNING">
            <paragraph>
                Title underline too short.
            <literal_block xml:space="preserve">
                Title
                ====
        <paragraph>
            Test short underline.
"""],
["""\
=====
Title
=====

Test overline title.
""",
"""\
<document source="test data">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            Test overline title.
"""],
["""\
=======
 Title
=======

Test overline title with inset.
""",
"""\
<document source="test data">
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            Test overline title with inset.
"""],
["""\
========================
 Test Missing Underline
""",
"""\
<document source="test data">
    <system_message level="4" line="1" source="test data" type="SEVERE">
        <paragraph>
            Incomplete section title.
        <literal_block xml:space="preserve">
            ========================
             Test Missing Underline
"""],
["""\
========================
 Test Missing Underline

""",
"""\
<document source="test data">
    <system_message level="4" line="1" source="test data" type="SEVERE">
        <paragraph>
            Missing matching underline for section title overline.
        <literal_block xml:space="preserve">
            ========================
             Test Missing Underline
"""],
["""\
=======
 Title

Test missing underline, with paragraph.
""",
"""\
<document source="test data">
    <system_message level="4" line="1" source="test data" type="SEVERE">
        <paragraph>
            Missing matching underline for section title overline.
        <literal_block xml:space="preserve">
            =======
             Title
    <paragraph>
        Test missing underline, with paragraph.
"""],
["""\
=======
 Long    Title
=======

Test long title and space normalization.
""",
"""\
<document source="test data">
    <section ids="long-title" names="long\ title">
        <title>
            Long    Title
        <system_message level="2" line="1" source="test data" type="WARNING">
            <paragraph>
                Title overline too short.
            <literal_block xml:space="preserve">
                =======
                 Long    Title
                =======
        <paragraph>
            Test long title and space normalization.
"""],
["""\
=======
 Title
-------

Paragraph.
""",
"""\
<document source="test data">
    <system_message level="4" line="1" source="test data" type="SEVERE">
        <paragraph>
            Title overline & underline mismatch.
        <literal_block xml:space="preserve">
            =======
             Title
            -------
    <paragraph>
        Paragraph.
"""],
["""\
========================

========================

Test missing titles; blank line in-between.

========================

========================
""",
"""\
<document source="test data">
    <transition>
    <transition>
    <paragraph>
        Test missing titles; blank line in-between.
    <transition>
    <transition>
"""],
["""\
========================
========================

Test missing titles; nothing in-between.

========================
========================
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Invalid section title or transition marker.
        <literal_block xml:space="preserve">
            ========================
            ========================
    <paragraph>
        Test missing titles; nothing in-between.
    <system_message level="3" line="6" source="test data" type="ERROR">
        <paragraph>
            Invalid section title or transition marker.
        <literal_block xml:space="preserve">
            ========================
            ========================
"""],
["""\
.. Test return to existing, highest-level section (Title 3).

Title 1
=======
Paragraph 1.

Title 2
-------
Paragraph 2.

Title 3
=======
Paragraph 3.

Title 4
-------
Paragraph 4.
""",
"""\
<document source="test data">
    <comment xml:space="preserve">
        Test return to existing, highest-level section (Title 3).
    <section ids="title-1" names="title\ 1">
        <title>
            Title 1
        <paragraph>
            Paragraph 1.
        <section ids="title-2" names="title\ 2">
            <title>
                Title 2
            <paragraph>
                Paragraph 2.
    <section ids="title-3" names="title\ 3">
        <title>
            Title 3
        <paragraph>
            Paragraph 3.
        <section ids="title-4" names="title\ 4">
            <title>
                Title 4
            <paragraph>
                Paragraph 4.
"""],
["""\
Test return to existing, highest-level section (Title 3, with overlines).

=======
Title 1
=======
Paragraph 1.

-------
Title 2
-------
Paragraph 2.

=======
Title 3
=======
Paragraph 3.

-------
Title 4
-------
Paragraph 4.
""",
"""\
<document source="test data">
    <paragraph>
        Test return to existing, highest-level section (Title 3, with overlines).
    <section ids="title-1" names="title\ 1">
        <title>
            Title 1
        <paragraph>
            Paragraph 1.
        <section ids="title-2" names="title\ 2">
            <title>
                Title 2
            <paragraph>
                Paragraph 2.
    <section ids="title-3" names="title\ 3">
        <title>
            Title 3
        <paragraph>
            Paragraph 3.
        <section ids="title-4" names="title\ 4">
            <title>
                Title 4
            <paragraph>
                Paragraph 4.
"""],
["""\
Test return to existing, higher-level section (Title 4).

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
    <paragraph>
        Test return to existing, higher-level section (Title 4).
    <section ids="title-1" names="title\ 1">
        <title>
            Title 1
        <paragraph>
            Paragraph 1.
        <section ids="title-2" names="title\ 2">
            <title>
                Title 2
            <paragraph>
                Paragraph 2.
            <section ids="title-3" names="title\ 3">
                <title>
                    Title 3
                <paragraph>
                    Paragraph 3.
        <section ids="title-4" names="title\ 4">
            <title>
                Title 4
            <paragraph>
                Paragraph 4.
"""],
["""\
Test bad subsection order (Title 4).

Title 1
=======
Paragraph 1.

Title 2
-------
Paragraph 2.

Title 3
=======
Paragraph 3.

Title 4
```````
Paragraph 4.
""",
"""\
<document source="test data">
    <paragraph>
        Test bad subsection order (Title 4).
    <section ids="title-1" names="title\ 1">
        <title>
            Title 1
        <paragraph>
            Paragraph 1.
        <section ids="title-2" names="title\ 2">
            <title>
                Title 2
            <paragraph>
                Paragraph 2.
    <section ids="title-3" names="title\ 3">
        <title>
            Title 3
        <paragraph>
            Paragraph 3.
        <system_message level="4" line="15" source="test data" type="SEVERE">
            <paragraph>
                Title level inconsistent:
            <literal_block xml:space="preserve">
                Title 4
                ```````
        <paragraph>
            Paragraph 4.
"""],
["""\
Test bad subsection order (Title 4, with overlines).

=======
Title 1
=======
Paragraph 1.

-------
Title 2
-------
Paragraph 2.

=======
Title 3
=======
Paragraph 3.

```````
Title 4
```````
Paragraph 4.
""",
"""\
<document source="test data">
    <paragraph>
        Test bad subsection order (Title 4, with overlines).
    <section ids="title-1" names="title\ 1">
        <title>
            Title 1
        <paragraph>
            Paragraph 1.
        <section ids="title-2" names="title\ 2">
            <title>
                Title 2
            <paragraph>
                Paragraph 2.
    <section ids="title-3" names="title\ 3">
        <title>
            Title 3
        <paragraph>
            Paragraph 3.
        <system_message level="4" line="19" source="test data" type="SEVERE">
            <paragraph>
                Title level inconsistent:
            <literal_block xml:space="preserve">
                ```````
                Title 4
                ```````
        <paragraph>
            Paragraph 4.
"""],
["""\
Title containing *inline* ``markup``
====================================

Paragraph.
""",
"""\
<document source="test data">
    <section ids="title-containing-inline-markup" names="title\ containing\ inline\ markup">
        <title>
            Title containing \n\
            <emphasis>
                inline
             \n\
            <literal>
                markup
        <paragraph>
            Paragraph.
"""],
["""\
1. Numbered Title
=================

Paragraph.
""",
"""\
<document source="test data">
    <section ids="numbered-title" names="1.\ numbered\ title">
        <title>
            1. Numbered Title
        <paragraph>
            Paragraph.
"""],
["""\
1. Item 1.
2. Item 2.
3. Numbered Title
=================

Paragraph.
""",
"""\
<document source="test data">
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item 1.
        <list_item>
            <paragraph>
                Item 2.
    <system_message level="2" line="3" source="test data" type="WARNING">
        <paragraph>
            Enumerated list ends without a blank line; unexpected unindent.
    <section ids="numbered-title" names="3.\ numbered\ title">
        <title>
            3. Numbered Title
        <paragraph>
            Paragraph.
"""],
["""\
ABC
===

Short title.
""",
"""\
<document source="test data">
    <section ids="abc" names="abc">
        <title>
            ABC
        <paragraph>
            Short title.
"""],
["""\
ABC
==

Underline too short.
""",
"""\
<document source="test data">
    <system_message level="1" line="2" source="test data" type="INFO">
        <paragraph>
            Possible title underline, too short for the title.
            Treating it as ordinary text because it's so short.
    <paragraph>
        ABC
        ==
    <paragraph>
        Underline too short.
"""],
["""\
==
ABC
==

Over & underline too short.
""",
"""\
<document source="test data">
    <system_message level="1" line="1" source="test data" type="INFO">
        <paragraph>
            Possible incomplete section title.
            Treating the overline as ordinary text because it's so short.
    <paragraph>
        ==
        ABC
        ==
    <paragraph>
        Over & underline too short.
"""],
["""\
==
ABC

Overline too short, no underline.
""",
"""\
<document source="test data">
    <system_message level="1" line="1" source="test data" type="INFO">
        <paragraph>
            Possible incomplete section title.
            Treating the overline as ordinary text because it's so short.
    <paragraph>
        ==
        ABC
    <paragraph>
        Overline too short, no underline.
"""],
["""\
==
ABC
""",
"""\
<document source="test data">
    <system_message level="1" line="1" source="test data" type="INFO">
        <paragraph>
            Possible incomplete section title.
            Treating the overline as ordinary text because it's so short.
    <paragraph>
        ==
        ABC
"""],
["""\
==
  Not a title: a definition list item.
""",
"""\
<document source="test data">
    <system_message level="1" line="1" source="test data" type="INFO">
        <paragraph>
            Possible incomplete section title.
            Treating the overline as ordinary text because it's so short.
    <definition_list>
        <definition_list_item>
            <term>
                ==
            <definition>
                <paragraph>
                    Not a title: a definition list item.
"""],
["""\
==
  Not a title: a definition list item.
--
  Another definition list item.  It's in a different list,
  but that's an acceptable limitation given that this will
  probably never happen in real life.

  The next line will trigger a warning:
==
""",
"""\
<document source="test data">
    <system_message level="1" line="1" source="test data" type="INFO">
        <paragraph>
            Possible incomplete section title.
            Treating the overline as ordinary text because it's so short.
    <definition_list>
        <definition_list_item>
            <term>
                ==
            <definition>
                <paragraph>
                    Not a title: a definition list item.
    <system_message level="2" line="3" source="test data" type="WARNING">
        <paragraph>
            Definition list ends without a blank line; unexpected unindent.
    <system_message level="1" line="3" source="test data" type="INFO">
        <paragraph>
            Possible incomplete section title.
            Treating the overline as ordinary text because it's so short.
    <definition_list>
        <definition_list_item>
            <term>
                --
            <definition>
                <paragraph>
                    Another definition list item.  It's in a different list,
                    but that's an acceptable limitation given that this will
                    probably never happen in real life.
                <paragraph>
                    The next line will trigger a warning:
    <system_message level="2" line="9" source="test data" type="WARNING">
        <paragraph>
            Definition list ends without a blank line; unexpected unindent.
    <paragraph>
        ==
"""],
["""\
Paragraph

    ==
    ABC
    ==

    Over & underline too short.
""",
"""\
<document source="test data">
    <paragraph>
        Paragraph
    <block_quote>
        <system_message level="1" line="3" source="test data" type="INFO">
            <paragraph>
                Unexpected possible title overline or transition.
                Treating it as ordinary text because it's so short.
        <paragraph>
            ==
            ABC
            ==
        <paragraph>
            Over & underline too short.
"""],
["""\
Paragraph

    ABC
    ==

    Underline too short.
""",
"""\
<document source="test data">
    <paragraph>
        Paragraph
    <block_quote>
        <paragraph>
            ABC
            ==
        <paragraph>
            Underline too short.
"""],
["""\
...
...

...
---

...
...
...
""",
"""\
<document source="test data">
    <system_message level="1" line="1" source="test data" type="INFO">
        <paragraph>
            Possible incomplete section title.
            Treating the overline as ordinary text because it's so short.
    <section dupnames="..." ids="id1">
        <title>
            ...
        <system_message level="1" line="4" source="test data" type="INFO">
            <paragraph>
                Possible incomplete section title.
                Treating the overline as ordinary text because it's so short.
        <section dupnames="..." ids="id2">
            <title>
                ...
            <system_message backrefs="id2" level="1" line="5" source="test data" type="INFO">
                <paragraph>
                    Duplicate implicit target name: "...".
            <system_message level="1" line="7" source="test data" type="INFO">
                <paragraph>
                    Possible incomplete section title.
                    Treating the overline as ordinary text because it's so short.
    <system_message level="1" line="7" source="test data" type="INFO">
        <paragraph>
            Possible incomplete section title.
            Treating the overline as ordinary text because it's so short.
    <section dupnames="..." ids="id3">
        <title>
            ...
        <system_message backrefs="id3" level="1" line="8" source="test data" type="INFO">
            <paragraph>
                Duplicate implicit target name: "...".
        <paragraph>
            ...
"""],
["""\
..
Hi
..

...
Yo
...

Ho
""",
"""\
<document source="test data">
    <comment xml:space="preserve">
    <system_message level="2" line="2" source="test data" type="WARNING">
        <paragraph>
            Explicit markup ends without a blank line; unexpected unindent.
    <section ids="hi" names="hi">
        <title>
            Hi
        <section ids="yo" names="yo">
            <title>
                Yo
            <paragraph>
                Ho
"""],
["""\
Empty Section
=============
""",
"""\
<document source="test data">
    <section ids="empty-section" names="empty\ section">
        <title>
            Empty Section
"""],
["""\
===
One
===

The bubble-up parser strategy conflicts with short titles
(<= 3 char-long over- & underlines).

===
Two
===

The parser currently contains a work-around kludge.
Without it, the parser ends up in an infinite loop.
""",
"""\
<document source="test data">
    <section ids="one" names="one">
        <title>
            One
        <paragraph>
            The bubble-up parser strategy conflicts with short titles
            (<= 3 char-long over- & underlines).
    <section ids="two" names="two">
        <title>
            Two
        <paragraph>
            The parser currently contains a work-around kludge.
            Without it, the parser ends up in an infinite loop.
"""],
["""\
""",
"""\
<document source="test data">
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
