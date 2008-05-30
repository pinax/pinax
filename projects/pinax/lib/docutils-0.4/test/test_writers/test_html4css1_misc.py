#! /usr/bin/env python

# Author: Felix Wiemann
# Contact: Felix_Wiemann@ososo.de
# Revision: $Revision: 3968 $
# Date: $Date: 2005-10-29 14:28:44 +0200 (Sat, 29 Oct 2005) $
# Copyright: This module has been placed in the public domain.

"""
Miscellaneous HTML writer tests.
"""

from __init__ import DocutilsTestSupport
from docutils import core


class EncodingTestCase(DocutilsTestSupport.StandardTestCase):

    def test_xmlcharrefreplace(self):
        # Test that xmlcharrefreplace is the default output encoding
        # error handler.
        settings_overrides={
            'output_encoding': 'latin1',
            'stylesheet': '',
            '_disable_config': 1,}
        result = core.publish_string(
            'EUR = \xe2\x82\xac', writer_name='html4css1',
            settings_overrides=settings_overrides)
        # Encoding a euro sign with latin1 doesn't work, so the
        # xmlcharrefreplcae handler is used.
        self.assert_(result.find('EUR = &#8364;') != -1)


if __name__ == '__main__':
    import unittest
    unittest.main()
