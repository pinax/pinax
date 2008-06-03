#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 3129 $
# Date: $Date: 2005-03-26 17:21:28 +0100 (Sat, 26 Mar 2005) $
# Copyright: This module has been placed in the public domain.

"""
Tests for interpreted text in docutils/parsers/rst/states.py.
"""

from __init__ import DocutilsTestSupport

def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

totest = {}

totest['basics'] = [
["""\
`interpreted`
""",
"""\
<document source="test data">
    <paragraph>
        <title_reference>
            interpreted
"""],
["""\
:title:`interpreted`
""",
"""\
<document source="test data">
    <paragraph>
        <title_reference>
            interpreted
"""],
["""\
`interpreted`:title:
""",
"""\
<document source="test data">
    <paragraph>
        <title_reference>
            interpreted
"""],
["""\
`interpreted \`title``
""",
"""\
<document source="test data">
    <paragraph>
        <title_reference>
            interpreted `title`
"""],
["""\
:title:`:not-role: interpreted`
""",
"""\
<document source="test data">
    <paragraph>
        <title_reference>
            :not-role: interpreted
"""],
["""\
`interpreted` but not \\`interpreted` [`] or ({[`] or [`]}) or `
""",
"""\
<document source="test data">
    <paragraph>
        <title_reference>
            interpreted
         but not `interpreted` [`] or ({[`] or [`]}) or `
"""],
["""\
`interpreted`-text `interpreted`: text `interpreted`:text `text`'s interpreted
""",
"""\
<document source="test data">
    <paragraph>
        <title_reference>
            interpreted
        -text \n\
        <title_reference>
            interpreted
        : text \n\
        <title_reference>
            interpreted
        :text \n\
        <title_reference>
            text
        's interpreted
"""],
["""\
`interpreted without closing backquote
""",
"""\
<document source="test data">
    <paragraph>
        <problematic ids="id2" refid="id1">
            `
        interpreted without closing backquote
    <system_message backrefs="id2" ids="id1" level="2" line="1" source="test data" type="WARNING">
        <paragraph>
            Inline interpreted text or phrase reference start-string without end-string.
"""],
["""\
`interpreted`:not a role if it contains whitespace:
""",
"""\
<document source="test data">
    <paragraph>
        <title_reference>
            interpreted
        :not a role if it contains whitespace:
"""],
["""\
:title:`` (empty interpteted text not recognized)
""",
"""\
<document source="test data">
    <paragraph>
        :title:`` (empty interpteted text not recognized)
"""],
["""\
Explicit roles for standard inline markup:
:emphasis:`emphasis`,
:strong:`strong`,
:literal:`inline literal text`.
""",
"""\
<document source="test data">
    <paragraph>
        Explicit roles for standard inline markup:
        <emphasis>
            emphasis
        ,
        <strong>
            strong
        ,
        <literal>
            inline literal text
        .
"""],
["""\
Simple explicit roles:
:ab:`abbreviation`,
:ac:`acronym`,
:sup:`superscript`,
:sub:`subscript`,
:title:`title reference`.
""",
"""\
<document source="test data">
    <paragraph>
        Simple explicit roles:
        <abbreviation>
            abbreviation
        ,
        <acronym>
            acronym
        ,
        <superscript>
            superscript
        ,
        <subscript>
            subscript
        ,
        <title_reference>
            title reference
        .
"""],
]

totest['references'] = [
["""\
:PEP:`0`
""",
"""\
<document source="test data">
    <paragraph>
        <reference refuri="http://www.python.org/peps/pep-0000.html">
            PEP 0
"""],
["""\
:PEP:`-1`
""",
"""\
<document source="test data">
    <paragraph>
        <problematic ids="id2" refid="id1">
            :PEP:`-1`
    <system_message backrefs="id2" ids="id1" level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            PEP number must be a number from 0 to 9999; "-1" is invalid.
"""],
["""\
:RFC:`2822`
""",
"""\
<document source="test data">
    <paragraph>
        <reference refuri="http://www.faqs.org/rfcs/rfc2822.html">
            RFC 2822
"""],
["""\
:RFC:`0`
""",
"""\
<document source="test data">
    <paragraph>
        <problematic ids="id2" refid="id1">
            :RFC:`0`
    <system_message backrefs="id2" ids="id1" level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            RFC number must be a number greater than or equal to 1; "0" is invalid.
"""],
]

totest['unknown_roles'] = [
["""\
:role:`interpreted`
""",
"""\
<document source="test data">
    <paragraph>
        <problematic ids="id2" refid="id1">
            :role:`interpreted`
    <system_message level="1" line="1" source="test data" type="INFO">
        <paragraph>
            No role entry for "role" in module "docutils.parsers.rst.languages.en".
            Trying "role" as canonical role name.
    <system_message backrefs="id2" ids="id1" level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Unknown interpreted text role "role".
"""],
["""\
`interpreted`:role:
""",
"""\
<document source="test data">
    <paragraph>
        <problematic ids="id2" refid="id1">
            `interpreted`:role:
    <system_message level="1" line="1" source="test data" type="INFO">
        <paragraph>
            No role entry for "role" in module "docutils.parsers.rst.languages.en".
            Trying "role" as canonical role name.
    <system_message backrefs="id2" ids="id1" level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Unknown interpreted text role "role".
"""],
["""\
:role:`interpreted`:role:
""",
"""\
<document source="test data">
    <paragraph>
        <problematic ids="id2" refid="id1">
            :role:`interpreted`:role:
    <system_message backrefs="id2" ids="id1" level="2" line="1" source="test data" type="WARNING">
        <paragraph>
            Multiple roles in interpreted text (both prefix and suffix present; only one allowed).
"""],
["""\
:very.long-role_name:`interpreted`
""",
"""\
<document source="test data">
    <paragraph>
        <problematic ids="id2" refid="id1">
            :very.long-role_name:`interpreted`
    <system_message level="1" line="1" source="test data" type="INFO">
        <paragraph>
            No role entry for "very.long-role_name" in module "docutils.parsers.rst.languages.en".
            Trying "very.long-role_name" as canonical role name.
    <system_message backrefs="id2" ids="id1" level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Unknown interpreted text role "very.long-role_name".
"""],
["""\
:restructuredtext-unimplemented-role:`interpreted`
""",
"""\
<document source="test data">
    <paragraph>
        <problematic ids="id2" refid="id1">
            :restructuredtext-unimplemented-role:`interpreted`
    <system_message level="1" line="1" source="test data" type="INFO">
        <paragraph>
            No role entry for "restructuredtext-unimplemented-role" in module "docutils.parsers.rst.languages.en".
            Trying "restructuredtext-unimplemented-role" as canonical role name.
    <system_message backrefs="id2" ids="id1" level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Interpreted text role "restructuredtext-unimplemented-role" not implemented.
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
