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

totest['enumerated_lists'] = [
["""\
1. Item one.

2. Item two.

3. Item three.
""",
"""\
<document source="test data">
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item one.
        <list_item>
            <paragraph>
                Item two.
        <list_item>
            <paragraph>
                Item three.
"""],
["""\
No blank lines betwen items:

1. Item one.
2. Item two.
3. Item three.
""",
"""\
<document source="test data">
    <paragraph>
        No blank lines betwen items:
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item one.
        <list_item>
            <paragraph>
                Item two.
        <list_item>
            <paragraph>
                Item three.
"""],
["""\
1.
empty item above, no blank line
""",
"""\
<document source="test data">
    <paragraph>
        1.
        empty item above, no blank line
"""],
["""\
Scrambled:

3. Item three.

2. Item two.

1. Item one.

3. Item three.
2. Item two.
1. Item one.
""",
"""\
<document source="test data">
    <paragraph>
        Scrambled:
    <enumerated_list enumtype="arabic" prefix="" start="3" suffix=".">
        <list_item>
            <paragraph>
                Item three.
    <system_message level="1" line="3" source="test data" type="INFO">
        <paragraph>
            Enumerated list start value not ordinal-1: "3" (ordinal 3)
    <enumerated_list enumtype="arabic" prefix="" start="2" suffix=".">
        <list_item>
            <paragraph>
                Item two.
    <system_message level="1" line="5" source="test data" type="INFO">
        <paragraph>
            Enumerated list start value not ordinal-1: "2" (ordinal 2)
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item one.
    <paragraph>
        3. Item three.
        2. Item two.
        1. Item one.
"""],
["""\
Skipping item 3:

1. Item 1.
2. Item 2.
4. Item 4.
""",
"""\
<document source="test data">
    <paragraph>
        Skipping item 3:
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item 1.
    <system_message level="2" line="4" source="test data" type="WARNING">
        <paragraph>
            Enumerated list ends without a blank line; unexpected unindent.
    <paragraph>
        2. Item 2.
        4. Item 4.
"""],
["""\
Start with non-ordinal-1:

0. Item zero.
1. Item one.
2. Item two.
3. Item three.

And again:

2. Item two.
3. Item three.
""",
"""\
<document source="test data">
    <paragraph>
        Start with non-ordinal-1:
    <enumerated_list enumtype="arabic" prefix="" start="0" suffix=".">
        <list_item>
            <paragraph>
                Item zero.
        <list_item>
            <paragraph>
                Item one.
        <list_item>
            <paragraph>
                Item two.
        <list_item>
            <paragraph>
                Item three.
    <system_message level="1" line="3" source="test data" type="INFO">
        <paragraph>
            Enumerated list start value not ordinal-1: "0" (ordinal 0)
    <paragraph>
        And again:
    <enumerated_list enumtype="arabic" prefix="" start="2" suffix=".">
        <list_item>
            <paragraph>
                Item two.
        <list_item>
            <paragraph>
                Item three.
    <system_message level="1" line="10" source="test data" type="INFO">
        <paragraph>
            Enumerated list start value not ordinal-1: "2" (ordinal 2)
"""],
["""\
1. Item one: line 1,
   line 2.
2. Item two: line 1,
   line 2.
3. Item three: paragraph 1, line 1,
   line 2.

   Paragraph 2.
""",
"""\
<document source="test data">
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item one: line 1,
                line 2.
        <list_item>
            <paragraph>
                Item two: line 1,
                line 2.
        <list_item>
            <paragraph>
                Item three: paragraph 1, line 1,
                line 2.
            <paragraph>
                Paragraph 2.
"""],
["""\
Different enumeration sequences:

1. Item 1.
2. Item 2.
3. Item 3.

A. Item A.
B. Item B.
C. Item C.

a. Item a.
b. Item b.
c. Item c.

I. Item I.
II. Item II.
III. Item III.

i. Item i.
ii. Item ii.
iii. Item iii.
""",
"""\
<document source="test data">
    <paragraph>
        Different enumeration sequences:
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item 1.
        <list_item>
            <paragraph>
                Item 2.
        <list_item>
            <paragraph>
                Item 3.
    <enumerated_list enumtype="upperalpha" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item A.
        <list_item>
            <paragraph>
                Item B.
        <list_item>
            <paragraph>
                Item C.
    <enumerated_list enumtype="loweralpha" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item a.
        <list_item>
            <paragraph>
                Item b.
        <list_item>
            <paragraph>
                Item c.
    <enumerated_list enumtype="upperroman" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item I.
        <list_item>
            <paragraph>
                Item II.
        <list_item>
            <paragraph>
                Item III.
    <enumerated_list enumtype="lowerroman" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item i.
        <list_item>
            <paragraph>
                Item ii.
        <list_item>
            <paragraph>
                Item iii.
"""],
["""\
Bad Roman numerals:

i. i

ii. ii

iii. iii

iiii. iiii
      second line

(LCD) is an acronym made up of Roman numerals

(livid) is a word made up of Roman numerals

(CIVIL) is another such word

(I) I

(IVXLCDM) IVXLCDM
""",
"""\
<document source="test data">
    <paragraph>
        Bad Roman numerals:
    <enumerated_list enumtype="lowerroman" prefix="" suffix=".">
        <list_item>
            <paragraph>
                i
        <list_item>
            <paragraph>
                ii
        <list_item>
            <paragraph>
                iii
    <definition_list>
        <definition_list_item>
            <term>
                iiii. iiii
            <definition>
                <paragraph>
                    second line
    <paragraph>
        (LCD) is an acronym made up of Roman numerals
    <paragraph>
        (livid) is a word made up of Roman numerals
    <paragraph>
        (CIVIL) is another such word
    <enumerated_list enumtype="upperroman" prefix="(" suffix=")">
        <list_item>
            <paragraph>
                I
    <paragraph>
        (IVXLCDM) IVXLCDM
"""],
["""\
Potentially ambiguous cases:

A. Item A.
B. Item B.
C. Item C.

I. Item I.
II. Item II.
III. Item III.

a. Item a.
b. Item b.
c. Item c.

i. Item i.
ii. Item ii.
iii. Item iii.

Phew! Safe!
""",
"""\
<document source="test data">
    <paragraph>
        Potentially ambiguous cases:
    <enumerated_list enumtype="upperalpha" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item A.
        <list_item>
            <paragraph>
                Item B.
        <list_item>
            <paragraph>
                Item C.
    <enumerated_list enumtype="upperroman" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item I.
        <list_item>
            <paragraph>
                Item II.
        <list_item>
            <paragraph>
                Item III.
    <enumerated_list enumtype="loweralpha" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item a.
        <list_item>
            <paragraph>
                Item b.
        <list_item>
            <paragraph>
                Item c.
    <enumerated_list enumtype="lowerroman" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item i.
        <list_item>
            <paragraph>
                Item ii.
        <list_item>
            <paragraph>
                Item iii.
    <paragraph>
        Phew! Safe!
"""],
["""\
Definitely ambiguous:

A. Item A.
B. Item B.
C. Item C.
D. Item D.
E. Item E.
F. Item F.
G. Item G.
H. Item H.
I. Item I.
II. Item II.
III. Item III.

a. Item a.
b. Item b.
c. Item c.
d. Item d.
e. Item e.
f. Item f.
g. Item g.
h. Item h.
i. Item i.
ii. Item ii.
iii. Item iii.
""",
"""\
<document source="test data">
    <paragraph>
        Definitely ambiguous:
    <enumerated_list enumtype="upperalpha" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item A.
        <list_item>
            <paragraph>
                Item B.
        <list_item>
            <paragraph>
                Item C.
        <list_item>
            <paragraph>
                Item D.
        <list_item>
            <paragraph>
                Item E.
        <list_item>
            <paragraph>
                Item F.
        <list_item>
            <paragraph>
                Item G.
        <list_item>
            <paragraph>
                Item H.
    <system_message level="2" line="11" source="test data" type="WARNING">
        <paragraph>
            Enumerated list ends without a blank line; unexpected unindent.
    <enumerated_list enumtype="upperroman" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item I.
        <list_item>
            <paragraph>
                Item II.
        <list_item>
            <paragraph>
                Item III.
    <enumerated_list enumtype="loweralpha" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item a.
        <list_item>
            <paragraph>
                Item b.
        <list_item>
            <paragraph>
                Item c.
        <list_item>
            <paragraph>
                Item d.
        <list_item>
            <paragraph>
                Item e.
        <list_item>
            <paragraph>
                Item f.
        <list_item>
            <paragraph>
                Item g.
        <list_item>
            <paragraph>
                Item h.
    <system_message level="2" line="23" source="test data" type="WARNING">
        <paragraph>
            Enumerated list ends without a blank line; unexpected unindent.
    <enumerated_list enumtype="lowerroman" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item i.
        <list_item>
            <paragraph>
                Item ii.
        <list_item>
            <paragraph>
                Item iii.
"""],
["""\
Different enumeration formats:

1. Item 1.
2. Item 2.
3. Item 3.

1) Item 1).
2) Item 2).
3) Item 3).

(1) Item (1).
(2) Item (2).
(3) Item (3).
""",
"""\
<document source="test data">
    <paragraph>
        Different enumeration formats:
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item 1.
        <list_item>
            <paragraph>
                Item 2.
        <list_item>
            <paragraph>
                Item 3.
    <enumerated_list enumtype="arabic" prefix="" suffix=")">
        <list_item>
            <paragraph>
                Item 1).
        <list_item>
            <paragraph>
                Item 2).
        <list_item>
            <paragraph>
                Item 3).
    <enumerated_list enumtype="arabic" prefix="(" suffix=")">
        <list_item>
            <paragraph>
                Item (1).
        <list_item>
            <paragraph>
                Item (2).
        <list_item>
            <paragraph>
                Item (3).
"""],
["""\
Nested enumerated lists:

1. Item 1.

   A) Item A).
   B) Item B).
   C) Item C).

2. Item 2.

   (a) Item (a).

       I) Item I).
       II) Item II).
       III) Item III).

   (b) Item (b).

   (c) Item (c).

       (i) Item (i).
       (ii) Item (ii).
       (iii) Item (iii).

3. Item 3.
""",
"""\
<document source="test data">
    <paragraph>
        Nested enumerated lists:
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item 1.
            <enumerated_list enumtype="upperalpha" prefix="" suffix=")">
                <list_item>
                    <paragraph>
                        Item A).
                <list_item>
                    <paragraph>
                        Item B).
                <list_item>
                    <paragraph>
                        Item C).
        <list_item>
            <paragraph>
                Item 2.
            <enumerated_list enumtype="loweralpha" prefix="(" suffix=")">
                <list_item>
                    <paragraph>
                        Item (a).
                    <enumerated_list enumtype="upperroman" prefix="" suffix=")">
                        <list_item>
                            <paragraph>
                                Item I).
                        <list_item>
                            <paragraph>
                                Item II).
                        <list_item>
                            <paragraph>
                                Item III).
                <list_item>
                    <paragraph>
                        Item (b).
                <list_item>
                    <paragraph>
                        Item (c).
                    <enumerated_list enumtype="lowerroman" prefix="(" suffix=")">
                        <list_item>
                            <paragraph>
                                Item (i).
                        <list_item>
                            <paragraph>
                                Item (ii).
                        <list_item>
                            <paragraph>
                                Item (iii).
        <list_item>
            <paragraph>
                Item 3.
"""],
[u"""\
A. Einstein was a great influence on
B. Physicist, who was a colleague of
C. Chemist.  They all worked in
Princeton, NJ.

Using a non-breaking space as a workaround:

A.\u00a0Einstein was a great influence on
B. Physicist, who was a colleague of
C. Chemist.  They all worked in
Princeton, NJ.
""",
"""\
<document source="test data">
    <enumerated_list enumtype="upperalpha" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Einstein was a great influence on
        <list_item>
            <paragraph>
                Physicist, who was a colleague of
    <system_message level="2" line="3" source="test data" type="WARNING">
        <paragraph>
            Enumerated list ends without a blank line; unexpected unindent.
    <paragraph>
        C. Chemist.  They all worked in
        Princeton, NJ.
    <paragraph>
        Using a non-breaking space as a workaround:
    <paragraph>
        A.\xa0Einstein was a great influence on
        B. Physicist, who was a colleague of
        C. Chemist.  They all worked in
        Princeton, NJ.
"""],
["""\
1. Item one: line 1,
   line 2.
2. Item two: line 1,
  line 2.
3. Item three: paragraph 1, line 1,
 line 2.

   Paragraph 2.
""",
"""\
<document source="test data">
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item one: line 1,
                line 2.
        <list_item>
            <paragraph>
                Item two: line 1,
    <system_message level="2" line="4" source="test data" type="WARNING">
        <paragraph>
            Enumerated list ends without a blank line; unexpected unindent.
    <block_quote>
        <paragraph>
            line 2.
    <system_message level="2" line="5" source="test data" type="WARNING">
        <paragraph>
            Block quote ends without a blank line; unexpected unindent.
    <enumerated_list enumtype="arabic" prefix="" start="3" suffix=".">
        <list_item>
            <paragraph>
                Item three: paragraph 1, line 1,
    <system_message level="1" line="5" source="test data" type="INFO">
        <paragraph>
            Enumerated list start value not ordinal-1: "3" (ordinal 3)
    <system_message level="2" line="6" source="test data" type="WARNING">
        <paragraph>
            Enumerated list ends without a blank line; unexpected unindent.
    <block_quote>
        <paragraph>
            line 2.
        <block_quote>
            <paragraph>
                Paragraph 2.
"""],
["""\
1. Item one.

#. Item two.

#. Item three.
""",
"""\
<document source="test data">
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item one.
        <list_item>
            <paragraph>
                Item two.
        <list_item>
            <paragraph>
                Item three.
"""],
["""\
a. Item one.
#. Item two.
#. Item three.
""",
"""\
<document source="test data">
    <enumerated_list enumtype="loweralpha" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item one.
        <list_item>
            <paragraph>
                Item two.
        <list_item>
            <paragraph>
                Item three.
"""],
["""\
i. Item one.
ii. Item two.
#. Item three.
""",
"""\
<document source="test data">
    <enumerated_list enumtype="lowerroman" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item one.
        <list_item>
            <paragraph>
                Item two.
        <list_item>
            <paragraph>
                Item three.
"""],
["""\
#. Item one.
#. Item two.
#. Item three.
""",
"""\
<document source="test data">
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item one.
        <list_item>
            <paragraph>
                Item two.
        <list_item>
            <paragraph>
                Item three.
"""],
["""\
1. Item one.
#. Item two.
3. Item three.
""",
"""\
<document source="test data">
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item one.
    <system_message level="2" line="2" source="test data" type="WARNING">
        <paragraph>
            Enumerated list ends without a blank line; unexpected unindent.
    <paragraph>
        #. Item two.
        3. Item three.
"""],
["""\
z.
x
""",
"""\
<document source="test data">
    <paragraph>
        z.
        x
"""],
["""\
3-space indent, with a trailing space:

1. \n\
   foo

3-space indent, no trailing space:

1.
   foo

2-space indent:

1.
  foo

1-space indent:

1.
 foo

0-space indent, not a list item:

1.
foo

No item content:

1.
""",
"""\
<document source="test data">
    <paragraph>
        3-space indent, with a trailing space:
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
            <paragraph>
                foo
    <paragraph>
        3-space indent, no trailing space:
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
            <paragraph>
                foo
    <paragraph>
        2-space indent:
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
            <paragraph>
                foo
    <paragraph>
        1-space indent:
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
            <paragraph>
                foo
    <paragraph>
        0-space indent, not a list item:
    <paragraph>
        1.
        foo
    <paragraph>
        No item content:
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
