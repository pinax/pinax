#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 3918 $
# Date: $Date: 2005-10-03 15:11:40 +0200 (Mon, 03 Oct 2005) $
# Copyright: This module has been placed in the public domain.

"""
Tests for states.py.
"""

from __init__ import DocutilsTestSupport

def suite():
    s = DocutilsTestSupport.SimpleTableParserTestSuite()
    s.generateTests(totest)
    return s

totest = {}

totest['simple_tables'] = [
["""\
============  ============
A table with  two columns.
============  ============
""",
([12, 12],
 [],
 [[[0, 0, 1, ['A table with']],
   [0, 0, 1, ['two columns.']]]])],
["""\
============  ============
A table with  two columns
and           two rows.
============  ============
""",
([12, 12],
 [],
 [[[0, 0, 1, ['A table with']],
   [0, 0, 1, ['two columns']]],
  [[0, 0, 2, ['and']],
   [0, 0, 2, ['two rows.']]]])],
["""\
==========  ===========
A table with four rows,
-----------------------
and two     columns.   
First and   last rows     
contain column spans.   
=======================
""",
([10, 11],
 [],
 [[[0, 1, 1, ['A table with four rows,']]],
  [[0, 0, 3, ['and two']],
   [0, 0, 3, ['columns.']]],
  [[0, 0, 4, ['First and']],
   [0, 0, 4, ['last rows']]],
  [[0, 1, 5, ['contain column spans.']]]])],
["""\
=======  =====  ======
A bad table     cell 2
cell 3          cell 4
============  ======
""",
'TableMarkupError: Text in column margin at line offset 1.'],
["""\
===========  ================
A table with two header rows,
-----------------------------
the first    with a span.    
===========  ================
Two body     rows,           
the second with a span.      
=============================
""",
([11, 16],
 [[[0, 1, 1, ['A table with two header rows,']]],
  [[0, 0, 3, ['the first']],
   [0, 0, 3, ['with a span.']]]],
 [[[0, 0, 5, ['Two body']],
   [0, 0, 5, ['rows,']]],
  [[0, 1, 6, ['the second with a span.']]]])],
["""\
============  =============
A table with  two head/body
============  =============
row           separators.
============  =============
That's bad.
============  =============
""",
'TableMarkupError: Multiple head/body row separators in table '
'(at line offset 2 and 4); only one allowed.'],
["""\
============  ============
============  ============
""",
([12, 12],
 [],
 [[[0, 0, 1, []],
   [0, 0, 1, []]]])],
# ["""\
# ==============  ==========
# Table with row  separators
# ==============  ==========
#                 and blank
# --------------  ----------
#                 entries
# --------------  ----------
#                 in first
# --------------  ----------
#                 columns.
# ==============  ==========
# """,
# '']
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
