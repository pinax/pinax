#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 4156 $
# Date: $Date: 2005-12-08 05:43:13 +0100 (Thu, 08 Dec 2005) $
# Copyright: This module has been placed in the public domain.

"""
Tests for the target-notes directives.
"""

from __init__ import DocutilsTestSupport

def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

totest = {}

totest['target-notes'] = [
["""\
.. target-notes::
""",
"""\
<document source="test data">
    <pending>
        .. internal attributes:
             .transform: docutils.transforms.references.TargetNotes
             .details:
"""],
["""\
.. target-notes:: :class: custom
""",
"""\
<document source="test data">
    <pending>
        .. internal attributes:
             .transform: docutils.transforms.references.TargetNotes
             .details:
               class: ['custom']
"""],
["""\
.. target-notes::
   :class:
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Error in "target-notes" directive:
            invalid option value: (option: "class"; value: None)
            argument required but none supplied.
        <literal_block xml:space="preserve">
            .. target-notes::
               :class:
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
