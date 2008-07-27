#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 3937 $
# Date: $Date: 2005-10-11 22:40:41 +0200 (Tue, 11 Oct 2005) $
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

totest['substitution_definitions'] = [
["""\
Here's an image substitution definition:

.. |symbol| image:: symbol.png
""",
"""\
<document source="test data">
    <paragraph>
        Here's an image substitution definition:
    <substitution_definition names="symbol">
        <image alt="symbol" uri="symbol.png">
"""],
["""\
Embedded directive starts on the next line:

.. |symbol|
   image:: symbol.png
""",
"""\
<document source="test data">
    <paragraph>
        Embedded directive starts on the next line:
    <substitution_definition names="symbol">
        <image alt="symbol" uri="symbol.png">
"""],
["""\
Trailing spaces should not be significant:

.. |symbol| image:: \n\
   symbol.png
""",
"""\
<document source="test data">
    <paragraph>
        Trailing spaces should not be significant:
    <substitution_definition names="symbol">
        <image alt="symbol" uri="symbol.png">
"""],
["""\
Here's a series of substitution definitions:

.. |symbol 1| image:: symbol1.png
.. |SYMBOL 2| image:: symbol2.png
   :height: 50
   :width: 100
.. |symbol 3| image:: symbol3.png
""",
"""\
<document source="test data">
    <paragraph>
        Here's a series of substitution definitions:
    <substitution_definition names="symbol\ 1">
        <image alt="symbol 1" uri="symbol1.png">
    <substitution_definition names="SYMBOL\ 2">
        <image alt="SYMBOL 2" height="50" uri="symbol2.png" width="100">
    <substitution_definition names="symbol\ 3">
        <image alt="symbol 3" uri="symbol3.png">
"""],
["""\
.. |very long substitution text,
   split across lines| image:: symbol.png
""",
"""\
<document source="test data">
    <substitution_definition names="very\ long\ substitution\ text,\ split\ across\ lines">
        <image alt="very long substitution text, split across lines" uri="symbol.png">
"""],
["""\
.. |symbol 1| image:: symbol.png

    Followed by a block quote.
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Error in "image" directive:
            no content permitted.
        <literal_block xml:space="preserve">
            image:: symbol.png
            \n\
                Followed by a block quote.
    <system_message level="2" line="1" source="test data" type="WARNING">
        <paragraph>
            Substitution definition "symbol 1" empty or invalid.
        <literal_block xml:space="preserve">
            .. |symbol 1| image:: symbol.png
            \n\
                Followed by a block quote.
"""],
["""\
.. |symbol 1| image:: symbol.png

Followed by a paragraph.

.. |symbol 2| image:: symbol.png

..

    Followed by a block quote.
""",
"""\
<document source="test data">
    <substitution_definition names="symbol\ 1">
        <image alt="symbol 1" uri="symbol.png">
    <paragraph>
        Followed by a paragraph.
    <substitution_definition names="symbol\ 2">
        <image alt="symbol 2" uri="symbol.png">
    <comment xml:space="preserve">
    <block_quote>
        <paragraph>
            Followed by a block quote.
"""],
[u"""\
Substitutions support case differences:

.. |eacute| replace:: \u00E9
.. |Eacute| replace:: \u00C9
""",
u"""\
<document source="test data">
    <paragraph>
        Substitutions support case differences:
    <substitution_definition names="eacute">
        \u00E9
    <substitution_definition names="Eacute">
        \u00C9
"""],
["""\
Raw substitution, backslashes should be preserved:

.. |alpha| raw:: latex

   $\\\\alpha$
""",
"""\
<document source="test data">
    <paragraph>
        Raw substitution, backslashes should be preserved:
    <substitution_definition names="alpha">
        <raw format="latex" xml:space="preserve">
            $\\\\alpha$
"""],
["""\
Here are some duplicate substitution definitions:

.. |symbol| image:: symbol.png
.. |symbol| image:: symbol.png
""",
"""\
<document source="test data">
    <paragraph>
        Here are some duplicate substitution definitions:
    <substitution_definition dupnames="symbol">
        <image alt="symbol" uri="symbol.png">
    <system_message level="3" line="4" source="test data" type="ERROR">
        <paragraph>
            Duplicate substitution definition name: "symbol".
    <substitution_definition names="symbol">
        <image alt="symbol" uri="symbol.png">
"""],
["""\
Here are some bad cases:

.. |symbol| image:: symbol.png
No blank line after.

.. |empty|

.. |unknown| directive:: symbol.png

.. |invalid 1| there's no directive here
.. |invalid 2| there's no directive here
   With some block quote text, line 1.
   And some more, line 2.

.. |invalid 3| there's no directive here

.. | bad name | bad data

.. |
""",
"""\
<document source="test data">
    <paragraph>
        Here are some bad cases:
    <substitution_definition names="symbol">
        <image alt="symbol" uri="symbol.png">
    <system_message level="2" line="4" source="test data" type="WARNING">
        <paragraph>
            Explicit markup ends without a blank line; unexpected unindent.
    <paragraph>
        No blank line after.
    <system_message level="2" line="6" source="test data" type="WARNING">
        <paragraph>
            Substitution definition "empty" missing contents.
        <literal_block xml:space="preserve">
            .. |empty|
    <system_message level="1" line="8" source="test data" type="INFO">
        <paragraph>
            No directive entry for "directive" in module "docutils.parsers.rst.languages.en".
            Trying "directive" as canonical directive name.
    <system_message level="3" line="8" source="test data" type="ERROR">
        <paragraph>
            Unknown directive type "directive".
        <literal_block xml:space="preserve">
            directive:: symbol.png
    <system_message level="2" line="8" source="test data" type="WARNING">
        <paragraph>
            Substitution definition "unknown" empty or invalid.
        <literal_block xml:space="preserve">
            .. |unknown| directive:: symbol.png
    <system_message level="2" line="10" source="test data" type="WARNING">
        <paragraph>
            Substitution definition "invalid 1" empty or invalid.
        <literal_block xml:space="preserve">
            .. |invalid 1| there's no directive here
    <system_message level="2" line="11" source="test data" type="WARNING">
        <paragraph>
            Substitution definition "invalid 2" empty or invalid.
        <literal_block xml:space="preserve">
            .. |invalid 2| there's no directive here
               With some block quote text, line 1.
               And some more, line 2.
    <system_message level="2" line="15" source="test data" type="WARNING">
        <paragraph>
            Substitution definition "invalid 3" empty or invalid.
        <literal_block xml:space="preserve">
            .. |invalid 3| there's no directive here
    <comment xml:space="preserve">
        | bad name | bad data
    <comment xml:space="preserve">
        |
"""],
["""\
Elements that are prohibited inside of substitution definitions:

.. |target| replace:: _`target`
.. |reference| replace:: anonymous__
.. |auto-numbered footnote| replace:: [#]_
""",
"""\
<document source="test data">
    <paragraph>
        Elements that are prohibited inside of substitution definitions:
    <system_message level="3" line="3" source="test data" type="ERROR">
        <paragraph>
            Substitution definition contains illegal element:
        <literal_block xml:space="preserve">
            <target ids="target" names="target">
                target
        <literal_block xml:space="preserve">
            .. |target| replace:: _`target`
    <system_message level="3" line="4" source="test data" type="ERROR">
        <paragraph>
            Substitution definition contains illegal element:
        <literal_block xml:space="preserve">
            <reference anonymous="1" name="anonymous">
                anonymous
        <literal_block xml:space="preserve">
            .. |reference| replace:: anonymous__
    <system_message level="3" line="5" source="test data" type="ERROR">
        <paragraph>
            Substitution definition contains illegal element:
        <literal_block xml:space="preserve">
            <footnote_reference auto="1" ids="id1">
        <literal_block xml:space="preserve">
            .. |auto-numbered footnote| replace:: [#]_
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
