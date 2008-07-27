#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 3129 $
# Date: $Date: 2005-03-26 17:21:28 +0100 (Sat, 26 Mar 2005) $
# Copyright: This module has been placed in the public domain.

"""
Tests for misc.py "role" directive.
"""

from __init__ import DocutilsTestSupport


def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

totest = {}

totest['role'] = [
["""\
.. role:: custom
.. role:: special

:custom:`interpreted` and :special:`interpreted`
""",
"""\
<document source="test data">
    <paragraph>
        <inline classes="custom">
            interpreted
         and \n\
        <inline classes="special">
            interpreted
"""],
["""\
.. role:: custom
   :class: custom-class
.. role:: special
   :class: special-class

:custom:`interpreted` and :special:`interpreted`
""",
"""\
<document source="test data">
    <paragraph>
        <inline classes="custom-class">
            interpreted
         and \n\
        <inline classes="special-class">
            interpreted
"""],
["""\
Must define :custom:`interpreted` before using it.

.. role:: custom

Now that it's defined, :custom:`interpreted` works.
""",
"""\
<document source="test data">
    <paragraph>
        Must define 
        <problematic ids="id2" refid="id1">
            :custom:`interpreted`
         before using it.
    <system_message level="1" line="1" source="test data" type="INFO">
        <paragraph>
            No role entry for "custom" in module "docutils.parsers.rst.languages.en".
            Trying "custom" as canonical role name.
    <system_message backrefs="id2" ids="id1" level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Unknown interpreted text role "custom".
    <paragraph>
        Now that it's defined, \n\
        <inline classes="custom">
            interpreted
         works.
"""],
["""\
.. role:: custom(emphasis)

:custom:`text`
""",
"""\
<document source="test data">
    <paragraph>
        <emphasis classes="custom">
            text
"""],
["""\
.. role:: custom ( emphasis )

:custom:`text`
""",
"""\
<document source="test data">
    <paragraph>
        <emphasis classes="custom">
            text
"""],
["""\
.. role:: custom(emphasis)
   :class: special

:custom:`text`
""",
"""\
<document source="test data">
    <paragraph>
        <emphasis classes="special">
            text
"""],
["""\
.. role:: custom(unknown-role)
""",
"""\
<document source="test data">
    <system_message level="1" line="1" source="test data" type="INFO">
        <paragraph>
            No role entry for "unknown-role" in module "docutils.parsers.rst.languages.en".
            Trying "unknown-role" as canonical role name.
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Unknown interpreted text role "unknown-role".
        <literal_block xml:space="preserve">
            .. role:: custom(unknown-role)
"""],
["""\
.. role:: custom
   :class: 1
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Error in "role" directive:
            invalid option value: (option: "class"; value: '1')
            cannot make "1" into a class name.
        <literal_block xml:space="preserve">
            .. role:: custom
               :class: 1
"""],
["""\
.. role:: 1
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Invalid argument for "role" directive:
            cannot make "1" into a class name.
        <literal_block xml:space="preserve">
            .. role:: 1
"""],
["""\
Test
----

.. role:: fileref(emphasis)

Testing a :fileref:`role` in a nested parse.
""",
"""\
<document source="test data">
    <section ids="test" names="test">
        <title>
            Test
        <paragraph>
            Testing a \n\
            <emphasis classes="fileref">
                role
             in a nested parse.
"""],
]

totest['raw_role'] = [
["""\
.. role:: html(raw)
   :format: html

Here's some :html:`<i>raw HTML data</i>`.
""",
"""\
<document source="test data">
    <paragraph>
        Here's some \n\
        <raw classes="html" format="html" xml:space="preserve">
            <i>raw HTML data</i>
        .
"""],
["""\
.. role:: itex(raw)
   :format: latex html

Here's some itex markup: :itex:`$x^\\infty$`.
""",
"""\
<document source="test data">
    <paragraph>
        Here's some itex markup: \n\
        <raw classes="itex" format="latex html" xml:space="preserve">
            $x^\\infty$
        .
"""],
["""\
Can't use the :raw:`role` directly.
""",
"""\
<document source="test data">
    <paragraph>
        Can't use the \n\
        <problematic ids="id2" refid="id1">
            :raw:`role`
         directly.
    <system_message backrefs="id2" ids="id1" level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            No format (Writer name) is associated with this role: "raw".
            The "raw" role cannot be used directly.
            Instead, use the "role" directive to create a new role with an associated format.
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
