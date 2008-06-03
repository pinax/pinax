#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 778 $
# Date: $Date: 2002-10-09 02:51:53 +0200 (Wed, 09 Oct 2002) $
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

totest['bullet_lists'] = [
["""\
- item
""",
"""\
<document source="test data">
    <bullet_list bullet="-">
        <list_item>
            <paragraph>
                item
"""],
["""\
* item 1

* item 2
""",
"""\
<document source="test data">
    <bullet_list bullet="*">
        <list_item>
            <paragraph>
                item 1
        <list_item>
            <paragraph>
                item 2
"""],
["""\
No blank line between:

+ item 1
+ item 2
""",
"""\
<document source="test data">
    <paragraph>
        No blank line between:
    <bullet_list bullet="+">
        <list_item>
            <paragraph>
                item 1
        <list_item>
            <paragraph>
                item 2
"""],
["""\
- item 1, para 1.

  item 1, para 2.

- item 2
""",
"""\
<document source="test data">
    <bullet_list bullet="-">
        <list_item>
            <paragraph>
                item 1, para 1.
            <paragraph>
                item 1, para 2.
        <list_item>
            <paragraph>
                item 2
"""],
["""\
- item 1, line 1
  item 1, line 2
- item 2
""",
"""\
<document source="test data">
    <bullet_list bullet="-">
        <list_item>
            <paragraph>
                item 1, line 1
                item 1, line 2
        <list_item>
            <paragraph>
                item 2
"""],
["""\
Different bullets:

- item 1

+ item 2

* item 3
- item 4
""",
"""\
<document source="test data">
    <paragraph>
        Different bullets:
    <bullet_list bullet="-">
        <list_item>
            <paragraph>
                item 1
    <bullet_list bullet="+">
        <list_item>
            <paragraph>
                item 2
    <bullet_list bullet="*">
        <list_item>
            <paragraph>
                item 3
    <system_message level="2" line="8" source="test data" type="WARNING">
        <paragraph>
            Bullet list ends without a blank line; unexpected unindent.
    <bullet_list bullet="-">
        <list_item>
            <paragraph>
                item 4
"""],
["""\
- item
no blank line
""",
"""\
<document source="test data">
    <bullet_list bullet="-">
        <list_item>
            <paragraph>
                item
    <system_message level="2" line="2" source="test data" type="WARNING">
        <paragraph>
            Bullet list ends without a blank line; unexpected unindent.
    <paragraph>
        no blank line
"""],
["""\
-

empty item above
""",
"""\
<document source="test data">
    <bullet_list bullet="-">
        <list_item>
    <paragraph>
        empty item above
"""],
["""\
-
empty item above, no blank line
""",
"""\
<document source="test data">
    <bullet_list bullet="-">
        <list_item>
    <system_message level="2" line="2" source="test data" type="WARNING">
        <paragraph>
            Bullet list ends without a blank line; unexpected unindent.
    <paragraph>
        empty item above, no blank line
"""],
]

if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
