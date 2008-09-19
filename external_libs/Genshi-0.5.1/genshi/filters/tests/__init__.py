# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2008 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://genshi.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://genshi.edgewall.org/log/.

import doctest
import unittest

def suite():
    from genshi.filters.tests import html, i18n, transform
    suite = unittest.TestSuite()
    suite.addTest(html.suite())
    suite.addTest(i18n.suite())
    if hasattr(doctest, 'NORMALIZE_WHITESPACE'):
        suite.addTest(transform.suite())
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
