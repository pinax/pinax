#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 3129 $
# Date: $Date: 2005-03-26 17:21:28 +0100 (Sat, 26 Mar 2005) $
# Copyright: This module has been placed in the public domain.

"""
Tests for misc.py "replace" directive.
"""

from __init__ import DocutilsTestSupport


def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

totest = {}

totest['replace'] = [
["""\
Test the |name| directive.

.. |name| replace:: "**replace**"
""",
"""\
<document source="test data">
    <paragraph>
        Test the \n\
        <substitution_reference refname="name">
            name
         directive.
    <substitution_definition names="name">
        "
        <strong>
            replace
        "
"""],
["""\
.. |name| replace:: paragraph 1

                    paragraph 2
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Error in "replace" directive: may contain a single paragraph only.
    <system_message level="2" line="1" source="test data" type="WARNING">
        <paragraph>
            Substitution definition "name" empty or invalid.
        <literal_block xml:space="preserve">
            .. |name| replace:: paragraph 1
            
                                paragraph 2
"""],
["""\
.. |name| replace::
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            The "replace" directive is empty; content required.
    <system_message level="2" line="1" source="test data" type="WARNING">
        <paragraph>
            Substitution definition "name" empty or invalid.
        <literal_block xml:space="preserve">
            .. |name| replace::
"""],
["""\
.. |Python| replace:: Python, *the* best language around

.. _Python: http://www.python.org/

I recommend you try |Python|_.
""",
"""\
<document source="test data">
    <substitution_definition names="Python">
        Python, 
        <emphasis>
            the
         best language around
    <target ids="python" names="python" refuri="http://www.python.org/">
    <paragraph>
        I recommend you try 
        <reference refname="python">
            <substitution_reference refname="Python">
                Python
        .
"""],
["""\
.. |name| replace::  *error in **inline ``markup
""",
"""\
<document source="test data">
    <system_message ids="id1" level="2" line="1" source="test data" type="WARNING">
        <paragraph>
            Inline emphasis start-string without end-string.
    <system_message ids="id3" level="2" line="1" source="test data" type="WARNING">
        <paragraph>
            Inline strong start-string without end-string.
    <system_message ids="id5" level="2" line="1" source="test data" type="WARNING">
        <paragraph>
            Inline literal start-string without end-string.
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Error in "replace" directive: may contain a single paragraph only.
    <system_message level="2" line="1" source="test data" type="WARNING">
        <paragraph>
            Substitution definition "name" empty or invalid.
        <literal_block xml:space="preserve">
            .. |name| replace::  *error in **inline ``markup
"""],
["""\
.. replace:: not valid outside of a substitution definition
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Invalid context: the "replace" directive can only be used within a substitution definition.
        <literal_block xml:space="preserve">
            .. replace:: not valid outside of a substitution definition
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
