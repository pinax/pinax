#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 3352 $
# Date: $Date: 2005-05-19 00:31:15 +0200 (Thu, 19 May 2005) $
# Copyright: This module has been placed in the public domain.

"""
Tests for images.py figure directives.
"""

from __init__ import DocutilsTestSupport

def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

totest = {}

totest['figures'] = [
["""\
.. figure:: picture.png
""",
"""\
<document source="test data">
    <figure>
        <image uri="picture.png">
"""],
["""\
.. figure:: picture.png

   A picture with a caption.
""",
"""\
<document source="test data">
    <figure>
        <image uri="picture.png">
        <caption>
            A picture with a caption.
"""],
["""\
.. figure:: picture.png

   - A picture with an invalid caption.
""",
"""\
<document source="test data">
    <figure>
        <image uri="picture.png">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Figure caption must be a paragraph or empty comment.
        <literal_block xml:space="preserve">
            .. figure:: picture.png
            \n\
               - A picture with an invalid caption.
"""],
["""\
.. figure:: picture.png

   ..

   A picture with a legend but no caption.
""",
"""\
<document source="test data">
    <figure>
        <image uri="picture.png">
        <legend>
            <paragraph>
                A picture with a legend but no caption.
"""],
["""\
.. Figure:: picture.png
   :height: 100
   :width: 200
   :scale: 50

   A picture with image options and a caption.
""",
"""\
<document source="test data">
    <figure>
        <image height="100" scale="50" uri="picture.png" width="200">
        <caption>
            A picture with image options and a caption.
"""],
["""\
.. Figure:: picture.png
   :height: 100
   :alt: alternate text
   :width: 200
   :scale: 50
   :figwidth: 300
   :figclass: class1 class2

   A picture with image options on individual lines, and this caption.
""",
"""\
<document source="test data">
    <figure classes="class1 class2" width="300">
        <image alt="alternate text" height="100" scale="50" uri="picture.png" width="200">
        <caption>
            A picture with image options on individual lines, and this caption.
"""],
["""\
.. figure:: picture.png
   :align: center

   A figure with explicit alignment.
""",
"""\
<document source="test data">
    <figure align="center">
        <image uri="picture.png">
        <caption>
            A figure with explicit alignment.
"""],
["""\
.. figure:: picture.png
   :align: top

   A figure with wrong alignment.
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Error in "figure" directive:
            invalid option value: (option: "align"; value: 'top')
            "top" unknown; choose from "left", "center", or "right".
        <literal_block xml:space="preserve">
            .. figure:: picture.png
               :align: top
            
               A figure with wrong alignment.
"""],
["""\
This figure lacks a caption. It may still have a
"Figure 1."-style caption appended in the output.

.. figure:: picture.png
""",
"""\
<document source="test data">
    <paragraph>
        This figure lacks a caption. It may still have a
        "Figure 1."-style caption appended in the output.
    <figure>
        <image uri="picture.png">
"""],
["""\
.. figure:: picture.png

   A picture with a caption and a legend.

   +-----------------------+-----------------------+
   | Symbol                | Meaning               |
   +=======================+=======================+
   | .. image:: tent.png   | Campground            |
   +-----------------------+-----------------------+
   | .. image:: waves.png  | Lake                  |
   +-----------------------+-----------------------+
   | .. image:: peak.png   | Mountain              |
   +-----------------------+-----------------------+
""",
"""\
<document source="test data">
    <figure>
        <image uri="picture.png">
        <caption>
            A picture with a caption and a legend.
        <legend>
            <table>
                <tgroup cols="2">
                    <colspec colwidth="23">
                    <colspec colwidth="23">
                    <thead>
                        <row>
                            <entry>
                                <paragraph>
                                    Symbol
                            <entry>
                                <paragraph>
                                    Meaning
                    <tbody>
                        <row>
                            <entry>
                                <image uri="tent.png">
                            <entry>
                                <paragraph>
                                    Campground
                        <row>
                            <entry>
                                <image uri="waves.png">
                            <entry>
                                <paragraph>
                                    Lake
                        <row>
                            <entry>
                                <image uri="peak.png">
                            <entry>
                                <paragraph>
                                    Mountain
"""],
["""\
.. figure:: picture.png

   ..

   A picture with a legend but no caption.
   (The empty comment replaces the caption, which must
   be a single paragraph.)
""",
"""\
<document source="test data">
    <figure>
        <image uri="picture.png">
        <legend>
            <paragraph>
                A picture with a legend but no caption.
                (The empty comment replaces the caption, which must
                be a single paragraph.)
"""],
["""\
Testing for line-leaks:

.. figure:: picture.png

   A picture with a caption.
.. figure:: picture.png

   A picture with a caption.
.. figure:: picture.png

   A picture with a caption.
.. figure:: picture.png
.. figure:: picture.png
.. figure:: picture.png
.. figure:: picture.png

   A picture with a caption.

.. figure:: picture.png

.. figure:: picture.png

   A picture with a caption.

.. figure:: picture.png
""",
"""\
<document source="test data">
    <paragraph>
        Testing for line-leaks:
    <figure>
        <image uri="picture.png">
        <caption>
            A picture with a caption.
    <figure>
        <image uri="picture.png">
        <caption>
            A picture with a caption.
    <figure>
        <image uri="picture.png">
        <caption>
            A picture with a caption.
    <figure>
        <image uri="picture.png">
    <figure>
        <image uri="picture.png">
    <figure>
        <image uri="picture.png">
    <figure>
        <image uri="picture.png">
        <caption>
            A picture with a caption.
    <figure>
        <image uri="picture.png">
    <figure>
        <image uri="picture.png">
        <caption>
            A picture with a caption.
    <figure>
        <image uri="picture.png">
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
