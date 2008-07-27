#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 3129 $
# Date: $Date: 2005-03-26 17:21:28 +0100 (Sat, 26 Mar 2005) $
# Copyright: This module has been placed in the public domain.

"""
Tests for docutils.transforms.universal.Messages.
"""

from __init__ import DocutilsTestSupport
from docutils.transforms.universal import Messages
from docutils.transforms.references import Substitutions
from docutils.parsers.rst import Parser


def suite():
    parser = Parser()
    s = DocutilsTestSupport.TransformTestSuite(parser)
    s.generateTests(totest)
    return s

totest = {}

totest['system_message_sections'] = ((Substitutions, Messages), [
["""\
This |unknown substitution| will generate a system message, thanks to
the ``Substitutions`` transform. The ``Messages`` transform will
generate a "System Messages" section.

(A second copy of the system message is tacked on to the end of the
document by the test framework.)
""",
"""\
<document source="test data">
    <paragraph>
        This \n\
        <problematic ids="id2" refid="id1">
            |unknown substitution|
         will generate a system message, thanks to
        the \n\
        <literal>
            Substitutions
         transform. The \n\
        <literal>
            Messages
         transform will
        generate a "System Messages" section.
    <paragraph>
        (A second copy of the system message is tacked on to the end of the
        document by the test framework.)
    <section classes="system-messages">
        <title>
            Docutils System Messages
        <system_message backrefs="id2" ids="id1" level="3" line="1" source="test data" type="ERROR">
            <paragraph>
                Undefined substitution referenced: "unknown substitution".
"""],
])


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
