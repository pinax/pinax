#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 3915 $
# Date: $Date: 2005-10-02 03:06:42 +0200 (Sun, 02 Oct 2005) $
# Copyright: This module has been placed in the public domain.

"""
Tests for misc.py "unicode" directive.
"""

from __init__ import DocutilsTestSupport


def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

totest = {}

totest['unicode'] = [
["""
Insert an em-dash (|mdash|), a copyright symbol (|copy|), a non-breaking
space (|nbsp|), a backwards-not-equals (|bne|), and a captial omega (|Omega|).

.. |mdash| unicode:: 0x02014
.. |copy| unicode:: \\u00A9
.. |nbsp| unicode:: &#x000A0;
.. |bne| unicode:: U0003D U020E5
.. |Omega| unicode:: U+003A9
""",
u"""\
<document source="test data">
    <paragraph>
        Insert an em-dash (
        <substitution_reference refname="mdash">
            mdash
        ), a copyright symbol (
        <substitution_reference refname="copy">
            copy
        ), a non-breaking
        space (
        <substitution_reference refname="nbsp">
            nbsp
        ), a backwards-not-equals (
        <substitution_reference refname="bne">
            bne
        ), and a captial omega (
        <substitution_reference refname="Omega">
            Omega
        ).
    <substitution_definition names="mdash">
        \u2014
    <substitution_definition names="copy">
        \u00A9
    <substitution_definition names="nbsp">
        \u00A0
    <substitution_definition names="bne">
        =
        \u20e5
    <substitution_definition names="Omega">
        \u03a9
"""],
["""
Bad input:

.. |empty| unicode::
.. |empty too| unicode:: .. comment doesn't count as content
.. |not hex| unicode:: 0xHEX
.. |not all hex| unicode:: UABCX
.. unicode:: not in a substitution definition
""",
"""\
<document source="test data">
    <paragraph>
        Bad input:
    <system_message level="3" line="4" source="test data" type="ERROR">
        <paragraph>
            Error in "unicode" directive:
            1 argument(s) required, 0 supplied.
        <literal_block xml:space="preserve">
            unicode::
    <system_message level="2" line="4" source="test data" type="WARNING">
        <paragraph>
            Substitution definition "empty" empty or invalid.
        <literal_block xml:space="preserve">
            .. |empty| unicode::
    <system_message level="2" line="5" source="test data" type="WARNING">
        <paragraph>
            Substitution definition "empty too" empty or invalid.
        <literal_block xml:space="preserve">
            .. |empty too| unicode:: .. comment doesn't count as content
    <substitution_definition names="not\ hex">
        0xHEX
    <substitution_definition names="not\ all\ hex">
        UABCX
    <system_message level="3" line="8" source="test data" type="ERROR">
        <paragraph>
            Invalid context: the "unicode" directive can only be used within a substitution definition.
        <literal_block xml:space="preserve">
            .. unicode:: not in a substitution definition
"""],
["""
Testing comments and extra text.

Copyright |copy| 2003, |BogusMegaCorp (TM)|.

.. |copy| unicode:: 0xA9 .. copyright sign
.. |BogusMegaCorp (TM)| unicode:: BogusMegaCorp U+2122
   .. with trademark sign
""",
u"""\
<document source="test data">
    <paragraph>
        Testing comments and extra text.
    <paragraph>
        Copyright 
        <substitution_reference refname="copy">
            copy
         2003, 
        <substitution_reference refname="BogusMegaCorp (TM)">
            BogusMegaCorp (TM)
        .
    <substitution_definition names="copy">
        \u00A9
    <substitution_definition names="BogusMegaCorp\ (TM)">
        BogusMegaCorp
        \u2122
"""],
["""
.. |too big for int| unicode:: 0x111111111111111111
.. |too big for unicode| unicode:: 0x11111111
""",
"""\
<document source="test data">
    <system_message level="3" line="2" source="test data" type="ERROR">
        <paragraph>
            Invalid character code: 0x111111111111111111
            ValueError: %s
        <literal_block xml:space="preserve">
            unicode:: 0x111111111111111111
    <system_message level="2" line="2" source="test data" type="WARNING">
        <paragraph>
            Substitution definition "too big for int" empty or invalid.
        <literal_block xml:space="preserve">
            .. |too big for int| unicode:: 0x111111111111111111
    <system_message level="3" line="3" source="test data" type="ERROR">
        <paragraph>
            Invalid character code: 0x11111111
            %s
        <literal_block xml:space="preserve">
            unicode:: 0x11111111
    <system_message level="2" line="3" source="test data" type="WARNING">
        <paragraph>
            Substitution definition "too big for unicode" empty or invalid.
        <literal_block xml:space="preserve">
            .. |too big for unicode| unicode:: 0x11111111
""" % ([DocutilsTestSupport.exception_data(
            'unichr(int("111111111111111111", 16))')[0],
        'code too large (%s)' % DocutilsTestSupport.exception_data(
    'unichr(int("111111111111111111", 16))')[0]]
       [isinstance(DocutilsTestSupport.exception_data(
    'unichr(int("111111111111111111", 16))')[0], OverflowError)],
       DocutilsTestSupport.exception_data('unichr(int("11111111", 16))')[2])]
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
