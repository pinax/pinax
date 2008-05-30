#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 4213 $
# Date: $Date: 2005-12-14 15:51:59 +0100 (Wed, 14 Dec 2005) $
# Copyright: This module has been placed in the public domain.

"""
Tests for misc.py "raw" directive.
"""

import os.path
import sys
from __init__ import DocutilsTestSupport


def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

mydir = 'test_parsers/test_rst/test_directives/'
raw1 = os.path.join(mydir, 'raw1.txt')
utf_16_file = os.path.join(mydir, 'utf-16.csv')
utf_16_file_rel = DocutilsTestSupport.utils.relative_path(None, utf_16_file)

totest = {}

totest['raw'] = [
["""\
.. raw:: html

   <span>This is some plain old raw text.</span>
""",
"""\
<document source="test data">
    <raw format="html" xml:space="preserve">
        <span>This is some plain old raw text.</span>
"""],
["""\
.. raw:: html
   :file: %s
""" % raw1,
"""\
<document source="test data">
    <raw format="html" source="%s" xml:space="preserve">
        <p>This file is used by <tt>test_raw.py</tt>.</p>
""" % DocutilsTestSupport.utils.relative_path(None, raw1)],
["""\
.. raw:: html
   :file: rawfile.html
   :url: http://example.org/
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            The "file" and "url" options may not be simultaneously specified for the "raw" directive.
        <literal_block xml:space="preserve">
            .. raw:: html
               :file: rawfile.html
               :url: http://example.org/
"""],
["""\
.. raw:: html
   :file: rawfile.html

   <p>Can't have both content and file attribute.</p>
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            "raw" directive may not both specify an external file and have content.
        <literal_block xml:space="preserve">
            .. raw:: html
               :file: rawfile.html
            
               <p>Can't have both content and file attribute.</p>
"""],
[r"""
.. raw:: latex html
 
   \[ \sum_{n=1}^\infty \frac{1}{n} \text{ etc.} \]
""",
"""\
<document source="test data">
    <raw format="latex html" xml:space="preserve">
        \\[ \\sum_{n=1}^\\infty \\frac{1}{n} \\text{ etc.} \\]
"""],
["""\
.. raw:: html
   :file: %s
   :encoding: utf-16
""" % utf_16_file_rel,
"""\
<document source="test data">
    <raw format="html" source="%s" xml:space="preserve">
        "Treat", "Quantity", "Description"
        "Albatr\xb0\xdf", 2.99, "\xa1On a \\u03c3\\u03c4\\u03b9\\u03ba!"
        "Crunchy Frog", 1.49, "If we took the b\xf6nes out, it wouldn\\u2019t be
        crunchy, now would it?"
        "Gannet Ripple", 1.99, "\xbfOn a \\u03c3\\u03c4\\u03b9\\u03ba?"
""" % utf_16_file_rel],
["""\
Raw input file is UTF-16-encoded, and is not valid ASCII.

.. raw:: html
   :file: %s
   :encoding: ascii
""" % utf_16_file_rel,
"""\
<document source="test data">
    <paragraph>
        Raw input file is UTF-16-encoded, and is not valid ASCII.
    <system_message level="4" line="3" source="test data" type="SEVERE">
        <paragraph>
            Problem with "raw" directive:
            UnicodeError: Unable to decode input data.  Tried the following encodings: \'ascii\'.
            (UnicodeDecodeError: 'ascii' codec can't decode byte 0xfe in position 0: ordinal not in range(128))
        <literal_block xml:space="preserve">
            .. raw:: html
               :file: %s
               :encoding: ascii
""" % utf_16_file_rel],
["""\
.. raw:: html
   :encoding: utf-8

   Should the parser complain becau\xdfe there is no :file:?  BUG?
""",
"""\
<document source="test data">
    <raw format="html" xml:space="preserve">
        Should the parser complain becau\xdfe there is no :file:?  BUG?
"""],
]

# Skip tests whose output contains "UnicodeDecodeError" if we are not
# using Python 2.3 or higher.
if sys.version_info < (2, 3):
    for i in range(len(totest['raw'])):
        if totest['raw'][i][1].find('UnicodeDecodeError') != -1:
            del totest['raw'][i]
            print ("Test totest['raw'][%s] skipped; "
                   "Python 2.3+ required for expected output." % i)
            # Assume we have only one of these tests.
            break


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
