#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 3160 $
# Date: $Date: 2005-04-03 01:12:06 +0200 (Sun, 03 Apr 2005) $
# Copyright: This module has been placed in the public domain.

"""
Tests for states.py.
"""

import os
from __init__ import DocutilsTestSupport

def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

mydir = 'test_parsers/test_rst/'
include2 = os.path.join(mydir, 'test_directives/include2.txt')

totest = {}

totest['grid_tables'] = [
["""\
+-------------------------------------+
| A table with one cell and one line. |
+-------------------------------------+
""",
"""\
<document source="test data">
    <table>
        <tgroup cols="1">
            <colspec colwidth="37">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            A table with one cell and one line.
"""],
["""\
+-----------------------+
| A table with one cell |
| and two lines.        |
+-----------------------+
""",
"""\
<document source="test data">
    <table>
        <tgroup cols="1">
            <colspec colwidth="23">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            A table with one cell
                            and two lines.
"""],
["""\
+-----------------------+
| A malformed table. |
+-----------------------+
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Malformed table.
        <literal_block xml:space="preserve">
            +-----------------------+
            | A malformed table. |
            +-----------------------+
"""],
["""\
+------------------------+
| A well-formed | table. |
+------------------------+

+------------------------+
| This +----------+ too! |
+------------------------+
""",
"""\
<document source="test data">
    <table>
        <tgroup cols="1">
            <colspec colwidth="24">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            A well-formed | table.
    <table>
        <tgroup cols="1">
            <colspec colwidth="24">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            This +----------+ too!
"""],
["""\
+--------------+--------------+
| A table with | two columns. |
+--------------+--------------+
""",
"""\
<document source="test data">
    <table>
        <tgroup cols="2">
            <colspec colwidth="14">
            <colspec colwidth="14">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            A table with
                    <entry>
                        <paragraph>
                            two columns.
"""],
["""\
+--------------+
| A table with |
+--------------+
| two rows.    |
+--------------+
""",
"""\
<document source="test data">
    <table>
        <tgroup cols="1">
            <colspec colwidth="14">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            A table with
                <row>
                    <entry>
                        <paragraph>
                            two rows.
"""],
["""\
+--------------+-------------+
| A table with | two columns |
+--------------+-------------+
| and          | two rows.   |
+--------------+-------------+
""",
"""\
<document source="test data">
    <table>
        <tgroup cols="2">
            <colspec colwidth="14">
            <colspec colwidth="13">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            A table with
                    <entry>
                        <paragraph>
                            two columns
                <row>
                    <entry>
                        <paragraph>
                            and
                    <entry>
                        <paragraph>
                            two rows.
"""],
["""\
+--------------+---------------+
| A table with | two columns,  |
+--------------+---------------+
| two rows, and a column span. |
+------------------------------+
""",
"""\
<document source="test data">
    <table>
        <tgroup cols="2">
            <colspec colwidth="14">
            <colspec colwidth="15">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            A table with
                    <entry>
                        <paragraph>
                            two columns,
                <row>
                    <entry morecols="1">
                        <paragraph>
                            two rows, and a column span.
"""],
["""\
+--------------------------+
| A table with three rows, |
+------------+-------------+
| and two    | columns.    |
+------------+-------------+
| First and last rows      |
| contains column spans.   |
+--------------------------+
""",
"""\
<document source="test data">
    <table>
        <tgroup cols="2">
            <colspec colwidth="12">
            <colspec colwidth="13">
            <tbody>
                <row>
                    <entry morecols="1">
                        <paragraph>
                            A table with three rows,
                <row>
                    <entry>
                        <paragraph>
                            and two
                    <entry>
                        <paragraph>
                            columns.
                <row>
                    <entry morecols="1">
                        <paragraph>
                            First and last rows
                            contains column spans.
"""],
["""\
+--------------+--------------+
| A table with | two columns, |
+--------------+ and a row    |
| two rows,    | span.        |
+--------------+--------------+
""",
"""\
<document source="test data">
    <table>
        <tgroup cols="2">
            <colspec colwidth="14">
            <colspec colwidth="14">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            A table with
                    <entry morerows="1">
                        <paragraph>
                            two columns,
                            and a row
                            span.
                <row>
                    <entry>
                        <paragraph>
                            two rows,
"""],
["""\
+------------+-------------+---------------+
| A table    | two rows in | and row spans |
| with three +-------------+ to left and   |
| columns,   | the middle, | right.        |
+------------+-------------+---------------+
""",
"""\
<document source="test data">
    <table>
        <tgroup cols="3">
            <colspec colwidth="12">
            <colspec colwidth="13">
            <colspec colwidth="15">
            <tbody>
                <row>
                    <entry morerows="1">
                        <paragraph>
                            A table
                            with three
                            columns,
                    <entry>
                        <paragraph>
                            two rows in
                    <entry morerows="1">
                        <paragraph>
                            and row spans
                            to left and
                            right.
                <row>
                    <entry>
                        <paragraph>
                            the middle,
"""],
["""\
Complex spanning pattern (no edge knows all rows/cols):

+-----------+-------------------------+
| W/NW cell | N/NE cell               |
|           +-------------+-----------+
|           | Middle cell | E/SE cell |
+-----------+-------------+           |
| S/SE cell               |           |
+-------------------------+-----------+
""",
"""\
<document source="test data">
    <paragraph>
        Complex spanning pattern (no edge knows all rows/cols):
    <table>
        <tgroup cols="3">
            <colspec colwidth="11">
            <colspec colwidth="13">
            <colspec colwidth="11">
            <tbody>
                <row>
                    <entry morerows="1">
                        <paragraph>
                            W/NW cell
                    <entry morecols="1">
                        <paragraph>
                            N/NE cell
                <row>
                    <entry>
                        <paragraph>
                            Middle cell
                    <entry morerows="1">
                        <paragraph>
                            E/SE cell
                <row>
                    <entry morecols="1">
                        <paragraph>
                            S/SE cell
"""],
["""\
+------------------------+------------+----------+----------+
| Header row, column 1   | Header 2   | Header 3 | Header 4 |
+========================+============+==========+==========+
| body row 1, column 1   | column 2   | column 3 | column 4 |
+------------------------+------------+----------+----------+
| body row 2             | Cells may span columns.          |
+------------------------+------------+---------------------+
| body row 3             | Cells may  | - Table cells       |
+------------------------+ span rows. | - contain           |
| body row 4             |            | - body elements.    |
+------------------------+------------+---------------------+
""",
"""\
<document source="test data">
    <table>
        <tgroup cols="4">
            <colspec colwidth="24">
            <colspec colwidth="12">
            <colspec colwidth="10">
            <colspec colwidth="10">
            <thead>
                <row>
                    <entry>
                        <paragraph>
                            Header row, column 1
                    <entry>
                        <paragraph>
                            Header 2
                    <entry>
                        <paragraph>
                            Header 3
                    <entry>
                        <paragraph>
                            Header 4
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            body row 1, column 1
                    <entry>
                        <paragraph>
                            column 2
                    <entry>
                        <paragraph>
                            column 3
                    <entry>
                        <paragraph>
                            column 4
                <row>
                    <entry>
                        <paragraph>
                            body row 2
                    <entry morecols="2">
                        <paragraph>
                            Cells may span columns.
                <row>
                    <entry>
                        <paragraph>
                            body row 3
                    <entry morerows="1">
                        <paragraph>
                            Cells may
                            span rows.
                    <entry morecols="1" morerows="1">
                        <bullet_list bullet="-">
                            <list_item>
                                <paragraph>
                                    Table cells
                            <list_item>
                                <paragraph>
                                    contain
                            <list_item>
                                <paragraph>
                                    body elements.
                <row>
                    <entry>
                        <paragraph>
                            body row 4
"""],
["""\
+-----------------+--------+
| A simple table  | cell 2 |
+-----------------+--------+
| cell 3          | cell 4 |
+-----------------+--------+
No blank line after table.
""",
"""\
<document source="test data">
    <table>
        <tgroup cols="2">
            <colspec colwidth="17">
            <colspec colwidth="8">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            A simple table
                    <entry>
                        <paragraph>
                            cell 2
                <row>
                    <entry>
                        <paragraph>
                            cell 3
                    <entry>
                        <paragraph>
                            cell 4
    <system_message level="2" line="6" source="test data" type="WARNING">
        <paragraph>
            Blank line required after table.
    <paragraph>
        No blank line after table.
"""],
["""\
+-----------------+--------+
| A simple table  | cell 2 |
+-----------------+--------+
| cell 3          | cell 4 |
+-----------------+--------+
    Unexpected indent and no blank line after table.
""",
"""\
<document source="test data">
    <table>
        <tgroup cols="2">
            <colspec colwidth="17">
            <colspec colwidth="8">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            A simple table
                    <entry>
                        <paragraph>
                            cell 2
                <row>
                    <entry>
                        <paragraph>
                            cell 3
                    <entry>
                        <paragraph>
                            cell 4
    <system_message level="3" line="6" source="test data" type="ERROR">
        <paragraph>
            Unexpected indentation.
    <system_message level="2" line="6" source="test data" type="WARNING">
        <paragraph>
            Blank line required after table.
    <block_quote>
        <paragraph>
            Unexpected indent and no blank line after table.
"""],
["""\
+--------------+-------------+
| A bad table. |             |
+--------------+             |
| Cells must be rectangles.  |
+----------------------------+
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Malformed table.
            Malformed table; parse incomplete.
        <literal_block xml:space="preserve">
            +--------------+-------------+
            | A bad table. |             |
            +--------------+             |
            | Cells must be rectangles.  |
            +----------------------------+
"""],
["""\
+------------------------------+
| This table contains another. |
|                              |
| +-------------------------+  |
| | A table within a table. |  |
| +-------------------------+  |
+------------------------------+
""",
"""\
<document source="test data">
    <table>
        <tgroup cols="1">
            <colspec colwidth="30">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            This table contains another.
                        <table>
                            <tgroup cols="1">
                                <colspec colwidth="25">
                                <tbody>
                                    <row>
                                        <entry>
                                            <paragraph>
                                                A table within a table.
"""],
["""\
+------------------+--------+
| A simple table   |        |
+------------------+--------+
| with empty cells |        |
+------------------+--------+
""",
"""\
<document source="test data">
    <table>
        <tgroup cols="2">
            <colspec colwidth="18">
            <colspec colwidth="8">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            A simple table
                    <entry>
                <row>
                    <entry>
                        <paragraph>
                            with empty cells
                    <entry>
"""],
[("""\
+------------------------------------------------------------------------------+
| .. include::                                                                 |
%s
+------------------------------------------------------------------------------+
| (The first cell of this table may expand                                     |
| to accommodate long filesystem paths.)                                       |
+------------------------------------------------------------------------------+
""") % ('\n'.join(['|    %-70s    |' % include2[part * 70 : (part + 1) * 70]
                   for part in range(len(include2) / 70 + 1)])),
"""\
<document source="test data">
    <table>
        <tgroup cols="1">
            <colspec colwidth="78">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            Here are some paragraphs
                            that can appear at any level.
                        <paragraph>
                            This file (include2.txt) is used by
                            <literal>
                                test_include.py
                            .
                <row>
                    <entry>
                        <paragraph>
                            (The first cell of this table may expand
                            to accommodate long filesystem paths.)
"""],
[("""\
Something before.

+------------------------------------------------------------------------------+
| .. include::                                                                 |
%s
+------------------------------------------------------------------------------+

Something afterwards.

And more.
""") % ('\n'.join(['|    %-70s    |' % include2[part * 70 : (part + 1) * 70]
                   for part in range(len(include2) / 70 + 1)])),
"""\
<document source="test data">
    <paragraph>
        Something before.
    <table>
        <tgroup cols="1">
            <colspec colwidth="78">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            Here are some paragraphs
                            that can appear at any level.
                        <paragraph>
                            This file (include2.txt) is used by
                            <literal>
                                test_include.py
                            .
    <paragraph>
        Something afterwards.
    <paragraph>
        And more.
"""],
]

totest['simple_tables'] = [
["""\
============  ============
A table with  two columns.
============  ============

Paragraph.
""",
"""\
<document source="test data">
    <table>
        <tgroup cols="2">
            <colspec colwidth="12">
            <colspec colwidth="12">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            A table with
                    <entry>
                        <paragraph>
                            two columns.
    <paragraph>
        Paragraph.
"""],
["""\
============  ============
A table with  two columns
and           two rows.
============  ============
""",
"""\
<document source="test data">
    <table>
        <tgroup cols="2">
            <colspec colwidth="12">
            <colspec colwidth="12">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            A table with
                    <entry>
                        <paragraph>
                            two columns
                <row>
                    <entry>
                        <paragraph>
                            and
                    <entry>
                        <paragraph>
                            two rows.
"""],
["""\
============  ==============
A table with  two columns,
two rows, and a column span.
============================
""",
"""\
<document source="test data">
    <table>
        <tgroup cols="2">
            <colspec colwidth="12">
            <colspec colwidth="14">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            A table with
                    <entry>
                        <paragraph>
                            two columns,
                <row>
                    <entry morecols="1">
                        <paragraph>
                            two rows, and a column span.
"""],
["""\
==  ===========  ===========
1   A table with three rows,
--  ------------------------
2   and three    columns.
3   First and third rows
    contain column spans.

    This row is a multi-line row, and overflows to the right.
--  ------------------------
4   One last     row.
==  ===========  ===========
""",
"""\
<document source="test data">
    <table>
        <tgroup cols="3">
            <colspec colwidth="2">
            <colspec colwidth="11">
            <colspec colwidth="44">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            1
                    <entry morecols="1">
                        <paragraph>
                            A table with three rows,
                <row>
                    <entry>
                        <paragraph>
                            2
                    <entry>
                        <paragraph>
                            and three
                    <entry>
                        <paragraph>
                            columns.
                <row>
                    <entry>
                        <paragraph>
                            3
                    <entry morecols="1">
                        <paragraph>
                            First and third rows
                            contain column spans.
                        <paragraph>
                            This row is a multi-line row, and overflows to the right.
                <row>
                    <entry>
                        <paragraph>
                            4
                    <entry>
                        <paragraph>
                            One last
                    <entry>
                        <paragraph>
                            row.
"""],
["""\
=======  =========  ========
A table with three  columns.
==================  ========
""",
"""\
<document source="test data">
    <table>
        <tgroup cols="3">
            <colspec colwidth="7">
            <colspec colwidth="9">
            <colspec colwidth="8">
            <tbody>
                <row>
                    <entry morecols="1">
                        <paragraph>
                            A table with three
                    <entry>
                        <paragraph>
                            columns.
"""],
["""\
==============  ======
A simple table  with
no bottom       border
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Malformed table.
            No bottom table border found.
        <literal_block xml:space="preserve">
            ==============  ======
            A simple table  with
            no bottom       border
"""],
["""\
==============  ======
A simple table  cell 2
cell 3          cell 4
==============  ======
No blank line after table.
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Malformed table.
            No bottom table border found or no blank line after table bottom.
        <literal_block xml:space="preserve">
            ==============  ======
            A simple table  cell 2
            cell 3          cell 4
            ==============  ======
    <system_message level="2" line="5" source="test data" type="WARNING">
        <paragraph>
            Blank line required after table.
    <paragraph>
        No blank line after table.
"""],
["""\
==============  ======
A simple table  cell 2
==============  ======
cell 3          cell 4
==============  ======
No blank line after table.
""",
"""\
<document source="test data">
    <table>
        <tgroup cols="2">
            <colspec colwidth="14">
            <colspec colwidth="6">
            <thead>
                <row>
                    <entry>
                        <paragraph>
                            A simple table
                    <entry>
                        <paragraph>
                            cell 2
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            cell 3
                    <entry>
                        <paragraph>
                            cell 4
    <system_message level="2" line="6" source="test data" type="WARNING">
        <paragraph>
            Blank line required after table.
    <paragraph>
        No blank line after table.
"""],
["""\
==============  ======
A simple table  cell 2
cell 3          cell 4
==============  ======
    Unexpected indent and no blank line after table.
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Malformed table.
            No bottom table border found or no blank line after table bottom.
        <literal_block xml:space="preserve">
            ==============  ======
            A simple table  cell 2
            cell 3          cell 4
            ==============  ======
    <system_message level="2" line="5" source="test data" type="WARNING">
        <paragraph>
            Blank line required after table.
    <block_quote>
        <paragraph>
            Unexpected indent and no blank line after table.
"""],
["""\
==============  ======
A bad table     cell 2
cell 3          cell 4
============  ========
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Malformed table.
            Column span alignment problem at line offset 3.
        <literal_block xml:space="preserve">
            ==============  ======
            A bad table     cell 2
            cell 3          cell 4
            ============  ========
"""],
["""\
========  =========
A bad table  cell 2
cell 3       cell 4
========  =========
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Malformed table.
            Text in column margin at line offset 1.
        <literal_block xml:space="preserve">
            ========  =========
            A bad table  cell 2
            cell 3       cell 4
            ========  =========
"""],
["""\
==  ============================
1   This table contains another.
2   =======  ======  ========
    A table  within  a table.
    =======  ======  ========

    The outer table does have to
    have at least two columns
    though.
==  ============================
""",
"""\
<document source="test data">
    <table>
        <tgroup cols="2">
            <colspec colwidth="2">
            <colspec colwidth="28">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            1
                    <entry>
                        <paragraph>
                            This table contains another.
                <row>
                    <entry>
                        <paragraph>
                            2
                    <entry>
                        <table>
                            <tgroup cols="3">
                                <colspec colwidth="7">
                                <colspec colwidth="6">
                                <colspec colwidth="8">
                                <tbody>
                                    <row>
                                        <entry>
                                            <paragraph>
                                                A table
                                        <entry>
                                            <paragraph>
                                                within
                                        <entry>
                                            <paragraph>
                                                a table.
                        <paragraph>
                            The outer table does have to
                            have at least two columns
                            though.
"""],
["""\
================  ======
A simple table
with empty cells
================  ======
""",
"""\
<document source="test data">
    <table>
        <tgroup cols="2">
            <colspec colwidth="16">
            <colspec colwidth="6">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            A simple table
                    <entry>
                <row>
                    <entry>
                        <paragraph>
                            with empty cells
                    <entry>
"""],
["""\
==============  ========
   A table        with
==============  ========
   centered      cells.

==============  ========
""",
"""\
<document source="test data">
    <table>
        <tgroup cols="2">
            <colspec colwidth="14">
            <colspec colwidth="8">
            <thead>
                <row>
                    <entry>
                        <paragraph>
                            A table
                    <entry>
                        <paragraph>
                            with
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            centered
                    <entry>
                        <paragraph>
                            cells.
"""],
["""\
==============  ======
A simple table  this text extends to the right
cell 3          the bottom border below is too long
==============  ========
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Malformed table.
            Bottom/header table border does not match top border.
        <literal_block xml:space="preserve">
            ==============  ======
            A simple table  this text extends to the right
            cell 3          the bottom border below is too long
            ==============  ========
"""],
["""\
============  =================
A table with  row separators.
------------  -----------------

Blank line    before.
------------  -----------------

Blank lines   before and after.

------------  -----------------
Blank line    after.

============  =================
""",
"""\
<document source="test data">
    <table>
        <tgroup cols="2">
            <colspec colwidth="12">
            <colspec colwidth="17">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            A table with
                    <entry>
                        <paragraph>
                            row separators.
                <row>
                    <entry>
                        <paragraph>
                            Blank line
                    <entry>
                        <paragraph>
                            before.
                <row>
                    <entry>
                        <paragraph>
                            Blank lines
                    <entry>
                        <paragraph>
                            before and after.
                <row>
                    <entry>
                        <paragraph>
                            Blank line
                    <entry>
                        <paragraph>
                            after.
"""],
["""\
============  ====================
A table with  many row separators.
------------  --------------------
------------  --------------------

------------  --------------------
============  ====================
""",
"""\
<document source="test data">
    <table>
        <tgroup cols="2">
            <colspec colwidth="12">
            <colspec colwidth="20">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            A table with
                    <entry>
                        <paragraph>
                            many row separators.
                <row>
                    <entry>
                    <entry>
                <row>
                    <entry>
                    <entry>
                <row>
                    <entry>
                    <entry>
"""],
["""\
==  ===========  ===========
1   Span columns 2 & 3
--  ------------------------
2   Span columns 2 & 3
    ------------------------
3
==  ===========  ===========

==  ===========  ===========
1 Span cols 1&2  but not 3
---------------  -----------
2 Span cols 1&2  but not 3
---------------
3   no spans     here
==  ===========  ===========

==  ===========  ===========
1   Not a span   Not a span
    -----------  -----------
2
==  ===========  ===========
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Malformed table.
            Text in column margin at line offset 3.
        <literal_block xml:space="preserve">
            ==  ===========  ===========
            1   Span columns 2 & 3
            --  ------------------------
            2   Span columns 2 & 3
                ------------------------
            3
            ==  ===========  ===========
    <system_message level="3" line="9" source="test data" type="ERROR">
        <paragraph>
            Malformed table.
            Column span incomplete at line offset 4.
        <literal_block xml:space="preserve">
            ==  ===========  ===========
            1 Span cols 1&2  but not 3
            ---------------  -----------
            2 Span cols 1&2  but not 3
            ---------------
            3   no spans     here
            ==  ===========  ===========
    <table>
        <tgroup cols="3">
            <colspec colwidth="2">
            <colspec colwidth="11">
            <colspec colwidth="11">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            1
                    <entry>
                        <system_message level="4" line="20" source="test data" type="SEVERE">
                            <paragraph>
                                Unexpected section title.
                            <literal_block xml:space="preserve">
                                Not a span
                                -----------
                    <entry>
                        <system_message level="4" line="20" source="test data" type="SEVERE">
                            <paragraph>
                                Unexpected section title.
                            <literal_block xml:space="preserve">
                                Not a span
                                -----------
                <row>
                    <entry>
                        <paragraph>
                            2
                    <entry>
                    <entry>
"""],
["""\
=========  =====================================================================
Inclusion  .. include::
%s
Note       The first row of this table may expand
           to accommodate long filesystem paths.
=========  =====================================================================
""" % ('\n'.join(['              %-65s' % include2[part * 65 : (part + 1) * 65]
                  for part in range(len(include2) / 65 + 1)])),
"""\
<document source="test data">
    <table>
        <tgroup cols="2">
            <colspec colwidth="9">
            <colspec colwidth="69">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            Inclusion
                    <entry>
                        <paragraph>
                            Here are some paragraphs
                            that can appear at any level.
                        <paragraph>
                            This file (include2.txt) is used by
                            <literal>
                                test_include.py
                            .
                <row>
                    <entry>
                        <paragraph>
                            Note
                    <entry>
                        <paragraph>
                            The first row of this table may expand
                            to accommodate long filesystem paths.
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
