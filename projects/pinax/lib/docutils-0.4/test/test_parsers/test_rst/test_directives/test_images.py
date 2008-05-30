#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 3828 $
# Date: $Date: 2005-08-24 02:05:38 +0200 (Wed, 24 Aug 2005) $
# Copyright: This module has been placed in the public domain.

"""
Tests for images.py image directives.
"""

from __init__ import DocutilsTestSupport

def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

totest = {}

totest['images'] = [
["""\
.. image:: picture.png
""",
"""\
<document source="test data">
    <image uri="picture.png">
"""],
["""\
.. image::
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Error in "image" directive:
            1 argument(s) required, 0 supplied.
        <literal_block xml:space="preserve">
            .. image::
"""],
["""\
.. image:: one two three.png
""",
"""\
<document source="test data">
    <image uri="onetwothree.png">
"""],
["""\
.. image:: picture.png
   :height: 100
   :width: 200
   :scale: 50
""",
"""\
<document source="test data">
    <image height="100" scale="50" uri="picture.png" width="200">
"""],
["""\
.. image::
   picture.png
   :height: 100
   :width: 200
   :scale: 50
""",
"""\
<document source="test data">
    <image height="100" scale="50" uri="picture.png" width="200">
"""],
["""\
.. image::
   :height: 100
   :width: 200
   :scale: 50
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Error in "image" directive:
            1 argument(s) required, 0 supplied.
        <literal_block xml:space="preserve">
            .. image::
               :height: 100
               :width: 200
               :scale: 50
"""],
["""\
.. image:: a/very/long/path/to/
   picture.png
   :height: 100
   :width: 200
   :scale: 50
""",
"""\
<document source="test data">
    <image height="100" scale="50" uri="a/very/long/path/to/picture.png" width="200">
"""],
["""\
.. image:: picture.png
   :width: 200px
   :height: 100 em
""",
"""\
<document source="test data">
    <image height="100em" uri="picture.png" width="200px">
"""],
["""\
.. image:: picture.png
   :width: 50%
   :height: 10mm
""",
"""\
<document source="test data">
    <image height="10mm" uri="picture.png" width="50%">
"""],
["""\
.. image:: picture.png
   :width: 50%
   :height: 40%
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Error in "image" directive:
            invalid option value: (option: "height"; value: \'40%\')
            not a positive measure of one of the following units:
            "em" "ex" "px" "in" "cm" "mm" "pt" "pc" "".
        <literal_block xml:space="preserve">
            .. image:: picture.png
               :width: 50%
               :height: 40%
"""],
["""\
.. image:: picture.png
   :height: 100
   :width: 200
   :scale: 50
   :alt: Alternate text for the picture
""",
"""\
<document source="test data">
    <image alt="Alternate text for the picture" height="100" scale="50" uri="picture.png" width="200">
"""],
["""\
.. image:: picture.png
   :scale: - 50
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Error in "image" directive:
            invalid option value: (option: "scale"; value: '- 50')
            negative value; must be positive or zero.
        <literal_block xml:space="preserve">
            .. image:: picture.png
               :scale: - 50
"""],
["""\
.. image:: picture.png
   :scale:
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Error in "image" directive:
            invalid option value: (option: "scale"; value: None)
            %s.
        <literal_block xml:space="preserve">
            .. image:: picture.png
               :scale:
""" % DocutilsTestSupport.exception_data('int(None)')[1][0]],
["""\
.. image:: picture.png
   :scale 50
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Error in "image" directive:
            invalid option block.
        <literal_block xml:space="preserve">
            .. image:: picture.png
               :scale 50
"""],
["""\
.. image:: picture.png
   scale: 50
""",
"""\
<document source="test data">
    <image uri="picture.pngscale:50">
"""],
["""\
.. image:: picture.png
   :: 50
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Error in "image" directive:
            invalid option block.
        <literal_block xml:space="preserve">
            .. image:: picture.png
               :: 50
"""],
["""\
.. image:: picture.png
   :sale: 50
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Error in "image" directive:
            unknown option: "sale".
        <literal_block xml:space="preserve">
            .. image:: picture.png
               :sale: 50
"""],
["""\
.. image:: picture.png
   :scale is: 50
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Error in "image" directive:
            invalid option data: extension option field name may not contain multiple words.
        <literal_block xml:space="preserve">
            .. image:: picture.png
               :scale is: 50
"""],
["""\
.. image:: picture.png
   :scale: fifty
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Error in "image" directive:
            invalid option value: (option: "scale"; value: 'fifty')
            invalid literal for int(): fifty.
        <literal_block xml:space="preserve">
            .. image:: picture.png
               :scale: fifty
"""],
["""\
.. image:: picture.png
   :scale: 50
   :scale: 50
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Error in "image" directive:
            invalid option data: duplicate option "scale".
        <literal_block xml:space="preserve">
            .. image:: picture.png
               :scale: 50
               :scale: 50
"""],
["""\
.. image:: picture.png
   :alt:

(Empty "alt" option.)
""",
"""\
<document source="test data">
    <image alt="" uri="picture.png">
    <paragraph>
        (Empty "alt" option.)
"""],
["""\
.. image:: picture.png
   :target: bigpicture.png
""",
"""\
<document source="test data">
    <reference refuri="bigpicture.png">
        <image uri="picture.png">
"""],
["""\
.. image:: picture.png
   :target: indirect_
""",
"""\
<document source="test data">
    <reference name="indirect" refname="indirect">
        <image uri="picture.png">
"""],
["""\
.. image:: picture.png
   :target: a/multi/
            line/uri

.. image:: picture.png
   :target: `a multi line
            internal reference`_
""",
"""\
<document source="test data">
    <reference refuri="a/multi/line/uri">
        <image uri="picture.png">
    <reference name="a multi line internal reference" refname="a multi line internal reference">
        <image uri="picture.png">
"""],
["""\
.. image:: picture.png
   :target:
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Error in "image" directive:
            invalid option value: (option: "target"; value: None)
            argument required but none supplied.
        <literal_block xml:space="preserve">
            .. image:: picture.png
               :target:
"""],
["""\
.. image:: picture.png
   :align: left
""",
"""\
<document source="test data">
    <image align="left" uri="picture.png">
"""],
["""\
.. image:: picture.png
   :align: top
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Error in "image" directive: "top" is not a valid value for the "align" option.  Valid values for "align" are: "left", "center", "right".
        <literal_block xml:space="preserve">
            .. image:: picture.png
               :align: top
"""],
["""\
.. |img| image:: picture.png
   :align: top
""",
"""\
<document source="test data">
    <substitution_definition names="img">
        <image align="top" alt="img" uri="picture.png">
"""],
["""\
.. |img| image:: picture.png
   :align: left
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Error in "image" directive: "left" is not a valid value for the "align" option within a substitution definition.  Valid values for "align" are: "top", "middle", "bottom".
        <literal_block xml:space="preserve">
            image:: picture.png
               :align: left
    <system_message level="2" line="1" source="test data" type="WARNING">
        <paragraph>
            Substitution definition "img" empty or invalid.
        <literal_block xml:space="preserve">
            .. |img| image:: picture.png
               :align: left
"""],
[u"""\
.. image:: picture.png
   :align: \xe4
""",
u"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Error in "image" directive:
            invalid option value: (option: "align"; value: u\'\\xe4\')
            "\xe4" unknown; choose from "top", "middle", "bottom", "left", "center", or "right".
        <literal_block xml:space="preserve">
            .. image:: picture.png
               :align: \xe4
"""],
["""
.. image:: test.png
   :target: Uppercase_

.. _Uppercase: http://docutils.sourceforge.net/
""",
"""\
<document source="test data">
    <reference name="Uppercase" refname="uppercase">
        <image uri="test.png">
    <target ids="uppercase" names="uppercase" refuri="http://docutils.sourceforge.net/">
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
