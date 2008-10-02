# -*- coding: utf-8 -*-
"""
    Test suite for the token module
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2006-2007 by Georg Brandl.
    :license: BSD, see LICENSE for more details.
"""

import unittest
import StringIO
import sys

from pygments import token


class TokenTest(unittest.TestCase):

    def test_tokentype(self):
        e = self.assertEquals
        r = self.assertRaises

        t = token.String

        e(t.split(), [token.Token, token.Literal, token.String])

        e(t.__class__, token._TokenType)

    def test_functions(self):
        self.assert_(token.is_token_subtype(token.String, token.String))
        self.assert_(token.is_token_subtype(token.String, token.Literal))
        self.failIf(token.is_token_subtype(token.Literal, token.String))

        self.assert_(token.string_to_tokentype(token.String) is token.String)
        self.assert_(token.string_to_tokentype('') is token.Token)
        self.assert_(token.string_to_tokentype('String') is token.String)

    def test_sanity_check(self):
        try:
            try:
                old_stdout = sys.stdout
                sys.stdout = StringIO.StringIO()
                execfile(token.__file__.rstrip('c'), {'__name__': '__main__'})
            finally:
                sys.stdout = old_stdout
        except SystemExit:
            pass


if __name__ == '__main__':
    unittest.main()
