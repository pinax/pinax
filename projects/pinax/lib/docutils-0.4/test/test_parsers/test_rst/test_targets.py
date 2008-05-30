#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 3915 $
# Date: $Date: 2005-10-02 03:06:42 +0200 (Sun, 02 Oct 2005) $
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

totest['targets'] = [
["""\
.. _target:

(Internal hyperlink target.)
""",
"""\
<document source="test data">
    <target ids="target" names="target">
    <paragraph>
        (Internal hyperlink target.)
"""],
["""\
.. _optional space before colon :
""",
"""\
<document source="test data">
    <target ids="optional-space-before-colon" names="optional\ space\ before\ colon">
"""],
["""\
External hyperlink targets:

.. _one-liner: http://structuredtext.sourceforge.net

.. _starts-on-this-line: http://
                         structuredtext.
                         sourceforge.net

.. _entirely-below:
   http://structuredtext.
   sourceforge.net

.. _not-indirect: uri\\_
""",
"""\
<document source="test data">
    <paragraph>
        External hyperlink targets:
    <target ids="one-liner" names="one-liner" refuri="http://structuredtext.sourceforge.net">
    <target ids="starts-on-this-line" names="starts-on-this-line" refuri="http://structuredtext.sourceforge.net">
    <target ids="entirely-below" names="entirely-below" refuri="http://structuredtext.sourceforge.net">
    <target ids="not-indirect" names="not-indirect" refuri="uri_">
"""],
["""\
Indirect hyperlink targets:

.. _target1: reference_

.. _target2: `phrase-link reference`_
""",
"""\
<document source="test data">
    <paragraph>
        Indirect hyperlink targets:
    <target ids="target1" names="target1" refname="reference">
    <target ids="target2" names="target2" refname="phrase-link reference">
"""],
["""\
.. _a long target name:

.. _`a target name: including a colon (quoted)`:

.. _a target name\: including a colon (escaped):
""",
"""\
<document source="test data">
    <target ids="a-long-target-name" names="a\ long\ target\ name">
    <target ids="a-target-name-including-a-colon-quoted" names="a\ target\ name:\ including\ a\ colon\ (quoted)">
    <target ids="a-target-name-including-a-colon-escaped" names="a\ target\ name:\ including\ a\ colon\ (escaped)">
"""],
["""\
.. _a very long target name,
   split across lines:
.. _`and another,
   with backquotes`:
""",
"""\
<document source="test data">
    <target ids="a-very-long-target-name-split-across-lines" names="a\ very\ long\ target\ name,\ split\ across\ lines">
    <target ids="and-another-with-backquotes" names="and\ another,\ with\ backquotes">
"""],
["""\
External hyperlink:

.. _target: http://www.python.org/
""",
"""\
<document source="test data">
    <paragraph>
        External hyperlink:
    <target ids="target" names="target" refuri="http://www.python.org/">
"""],
["""\
.. _email: jdoe@example.com

.. _multi-line email: jdoe
   @example.com
""",
"""\
<document source="test data">
    <target ids="email" names="email" refuri="mailto:jdoe@example.com">
    <target ids="multi-line-email" names="multi-line\ email" refuri="mailto:jdoe@example.com">
"""],
["""\
Duplicate external targets (different URIs):

.. _target: first

.. _target: second
""",
"""\
<document source="test data">
    <paragraph>
        Duplicate external targets (different URIs):
    <target dupnames="target" ids="target" refuri="first">
    <system_message backrefs="id1" level="2" line="5" source="test data" type="WARNING">
        <paragraph>
            Duplicate explicit target name: "target".
    <target dupnames="target" ids="id1" refuri="second">
"""],
["""\
Duplicate external targets (same URIs):

.. _target: first

.. _target: first
""",
"""\
<document source="test data">
    <paragraph>
        Duplicate external targets (same URIs):
    <target ids="target" names="target" refuri="first">
    <system_message backrefs="id1" level="1" line="5" source="test data" type="INFO">
        <paragraph>
            Duplicate explicit target name: "target".
    <target dupnames="target" ids="id1" refuri="first">
"""],
["""\
Duplicate implicit targets.

Title
=====

Paragraph.

Title
=====

Paragraph.
""",
"""\
<document source="test data">
    <paragraph>
        Duplicate implicit targets.
    <section dupnames="title" ids="title">
        <title>
            Title
        <paragraph>
            Paragraph.
    <section dupnames="title" ids="id1">
        <title>
            Title
        <system_message backrefs="id1" level="1" line="9" source="test data" type="INFO">
            <paragraph>
                Duplicate implicit target name: "title".
        <paragraph>
            Paragraph.
"""],
["""\
Duplicate implicit/explicit targets.

Title
=====

.. _title:

Paragraph.
""",
"""\
<document source="test data">
    <paragraph>
        Duplicate implicit/explicit targets.
    <section dupnames="title" ids="title">
        <title>
            Title
        <system_message backrefs="id1" level="1" line="6" source="test data" type="INFO">
            <paragraph>
                Duplicate implicit target name: "title".
        <target ids="id1" names="title">
        <paragraph>
            Paragraph.
"""],
["""\
Duplicate explicit targets.

.. _title:

First.

.. _title:

Second.

.. _title:

Third.
""",
"""\
<document source="test data">
    <paragraph>
        Duplicate explicit targets.
    <target dupnames="title" ids="title">
    <paragraph>
        First.
    <system_message backrefs="id1" level="2" line="7" source="test data" type="WARNING">
        <paragraph>
            Duplicate explicit target name: "title".
    <target dupnames="title" ids="id1">
    <paragraph>
        Second.
    <system_message backrefs="id2" level="2" line="11" source="test data" type="WARNING">
        <paragraph>
            Duplicate explicit target name: "title".
    <target dupnames="title" ids="id2">
    <paragraph>
        Third.
"""],
["""\
Duplicate targets:

Target
======

Implicit section header target.

.. [target] Citation target.

.. [#target] Autonumber-labeled footnote target.

.. _target:

Explicit internal target.

.. _target: Explicit_external_target
""",
"""\
<document source="test data">
    <paragraph>
        Duplicate targets:
    <section dupnames="target" ids="target">
        <title>
            Target
        <paragraph>
            Implicit section header target.
        <citation dupnames="target" ids="id1">
            <label>
                target
            <system_message backrefs="id1" level="1" line="8" source="test data" type="INFO">
                <paragraph>
                    Duplicate implicit target name: "target".
            <paragraph>
                Citation target.
        <footnote auto="1" dupnames="target" ids="id2">
            <system_message backrefs="id2" level="2" line="10" source="test data" type="WARNING">
                <paragraph>
                    Duplicate explicit target name: "target".
            <paragraph>
                Autonumber-labeled footnote target.
        <system_message backrefs="id3" level="2" line="12" source="test data" type="WARNING">
            <paragraph>
                Duplicate explicit target name: "target".
        <target dupnames="target" ids="id3">
        <paragraph>
            Explicit internal target.
        <system_message backrefs="id4" level="2" line="16" source="test data" type="WARNING">
            <paragraph>
                Duplicate explicit target name: "target".
        <target dupnames="target" ids="id4" refuri="Explicit_external_target">
"""],
["""\
.. _unescaped colon at end:: no good

.. _:: no good either

.. _escaped colon\:: OK

.. _`unescaped colon, quoted:`: OK
""",
"""\
<document source="test data">
    <comment xml:space="preserve">
        _unescaped colon at end:: no good
    <system_message level="2" line="1" source="test data" type="WARNING">
        <paragraph>
            malformed hyperlink target.
    <comment xml:space="preserve">
        _:: no good either
    <system_message level="2" line="3" source="test data" type="WARNING">
        <paragraph>
            malformed hyperlink target.
    <target ids="escaped-colon" names="escaped\ colon:" refuri="OK">
    <target ids="unescaped-colon-quoted" names="unescaped\ colon,\ quoted:" refuri="OK">
"""],
]

totest['anonymous_targets'] = [
["""\
Anonymous external hyperlink target:

.. __: http://w3c.org/
""",
"""\
<document source="test data">
    <paragraph>
        Anonymous external hyperlink target:
    <target anonymous="1" ids="id1" refuri="http://w3c.org/">
"""],
["""\
Anonymous external hyperlink target:

__ http://w3c.org/
""",
"""\
<document source="test data">
    <paragraph>
        Anonymous external hyperlink target:
    <target anonymous="1" ids="id1" refuri="http://w3c.org/">
"""],
["""\
Anonymous indirect hyperlink target:

.. __: reference_
""",
"""\
<document source="test data">
    <paragraph>
        Anonymous indirect hyperlink target:
    <target anonymous="1" ids="id1" refname="reference">
"""],
["""\
Anonymous external hyperlink target, not indirect:

__ uri\\_

__ this URI ends with an underscore_
""",
"""\
<document source="test data">
    <paragraph>
        Anonymous external hyperlink target, not indirect:
    <target anonymous="1" ids="id1" refuri="uri_">
    <target anonymous="1" ids="id2" refuri="thisURIendswithanunderscore_">
"""],
["""\
Anonymous indirect hyperlink targets:

__ reference_
__ `a very long
   reference`_
""",
"""\
<document source="test data">
    <paragraph>
        Anonymous indirect hyperlink targets:
    <target anonymous="1" ids="id1" refname="reference">
    <target anonymous="1" ids="id2" refname="a very long reference">
"""],
["""\
Mixed anonymous & named indirect hyperlink targets:

__ reference_
.. __: reference_
__ reference_
.. _target1: reference_
no blank line

.. _target2: reference_
__ reference_
.. __: reference_
__ reference_
no blank line
""",
"""\
<document source="test data">
    <paragraph>
        Mixed anonymous & named indirect hyperlink targets:
    <target anonymous="1" ids="id1" refname="reference">
    <target anonymous="1" ids="id2" refname="reference">
    <target anonymous="1" ids="id3" refname="reference">
    <target ids="target1" names="target1" refname="reference">
    <system_message level="2" line="7" source="test data" type="WARNING">
        <paragraph>
            Explicit markup ends without a blank line; unexpected unindent.
    <paragraph>
        no blank line
    <target ids="target2" names="target2" refname="reference">
    <target anonymous="1" ids="id4" refname="reference">
    <target anonymous="1" ids="id5" refname="reference">
    <target anonymous="1" ids="id6" refname="reference">
    <system_message level="2" line="13" source="test data" type="WARNING">
        <paragraph>
            Explicit markup ends without a blank line; unexpected unindent.
    <paragraph>
        no blank line
"""],
["""\
.. _
""",
"""\
<document source="test data">
    <comment xml:space="preserve">
        _
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
