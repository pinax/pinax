#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 3915 $
# Date: $Date: 2005-10-02 03:06:42 +0200 (Sun, 02 Oct 2005) $
# Copyright: This module has been placed in the public domain.

"""
Tests for docutils.transforms.peps.
"""

from __init__ import DocutilsTestSupport
from docutils.transforms.peps import TargetNotes
from docutils.parsers.rst import Parser


def suite():
    parser = Parser()
    s = DocutilsTestSupport.TransformTestSuite(parser)
    s.generateTests(totest)
    return s

totest = {}

totest['target_notes'] = ((TargetNotes,), [
["""\
No references or targets exist, therefore
no "References" section should be generated.
""",
"""\
<document source="test data">
    <paragraph>
        No references or targets exist, therefore
        no "References" section should be generated.
"""],
["""\
A target exists, here's the reference_.
A "References" section should be generated.

.. _reference: http://www.example.org
""",
"""\
<document source="test data">
    <paragraph>
        A target exists, here's the \n\
        <reference name="reference" refname="reference">
            reference
         \n\
        <footnote_reference auto="1" ids="id3" refname="TARGET_NOTE: id2">
        .
        A "References" section should be generated.
    <target ids="reference" names="reference" refuri="http://www.example.org">
    <section ids="id1">
        <title>
            References
        <footnote auto="1" ids="id2" names="TARGET_NOTE:\ id2">
            <paragraph>
                <reference refuri="http://www.example.org">
                    http://www.example.org
"""],
])



if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
