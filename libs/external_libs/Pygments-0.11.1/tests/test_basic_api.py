# -*- coding: utf-8 -*-
"""
    Pygments basic API tests
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2006-2007 by Georg Brandl.
    :license: BSD, see LICENSE for more details.
"""

import os
import unittest
import StringIO
import random

from pygments import lexers, formatters, filters, format
from pygments.token import _TokenType, Text
from pygments.lexer import RegexLexer
from pygments.formatters.img import FontNotFound

test_content = [chr(i) for i in xrange(33, 128)] * 5
random.shuffle(test_content)
test_content = ''.join(test_content) + '\n'

class LexersTest(unittest.TestCase):

    def test_import_all(self):
        # instantiate every lexer, to see if the token type defs are correct
        for x in lexers.LEXERS.keys():
            c = getattr(lexers, x)()

    def test_lexer_classes(self):
        a = self.assert_
        ae = self.assertEquals
        # test that every lexer class has the correct public API
        for lexer in lexers._iter_lexerclasses():
            a(type(lexer.name) is str)
            for attr in 'aliases', 'filenames', 'alias_filenames', 'mimetypes':
                a(hasattr(lexer, attr))
                a(type(getattr(lexer, attr)) is list, "%s: %s attribute wrong" %
                                                      (lexer, attr))
            result = lexer.analyse_text("abc")
            a(isinstance(result, float) and 0.0 <= result <= 1.0)

            inst = lexer(opt1="val1", opt2="val2")
            if issubclass(lexer, RegexLexer):
                if not hasattr(lexer, '_tokens'):
                    # if there's no "_tokens", the lexer has to be one with
                    # multiple tokendef variants
                    a(lexer.token_variants)
                    for variant in lexer.tokens:
                        a('root' in lexer.tokens[variant])
                else:
                    a('root' in lexer._tokens, '%s has no root state' % lexer)

            tokens = list(inst.get_tokens(test_content))
            txt = ""
            for token in tokens:
                a(isinstance(token, tuple))
                a(isinstance(token[0], _TokenType))
                if isinstance(token[1], str):
                    print repr(token[1])
                a(isinstance(token[1], unicode))
                txt += token[1]
            ae(txt, test_content, "%s lexer roundtrip failed: %r != %r" %
                    (lexer.name, test_content, txt))

    def test_get_lexers(self):
        a = self.assert_
        ae = self.assertEquals
        # test that the lexers functions work

        for func, args in [(lexers.get_lexer_by_name, ("python",)),
                           (lexers.get_lexer_for_filename, ("test.py",)),
                           (lexers.get_lexer_for_mimetype, ("text/x-python",)),
                           (lexers.guess_lexer, ("#!/usr/bin/python -O\nprint",)),
                           (lexers.guess_lexer_for_filename, ("a.py", "<%= @foo %>"))
                           ]:
            x = func(opt="val", *args)
            a(isinstance(x, lexers.PythonLexer))
            ae(x.options["opt"], "val")


class FiltersTest(unittest.TestCase):

    def test_basic(self):
        filter_args = {
            'whitespace': {'spaces': True, 'tabs': True, 'newlines': True},
            'highlight': {'names': ['isinstance', 'lexers', 'x']},
        }
        for x in filters.FILTERS.keys():
            lx = lexers.PythonLexer()
            lx.add_filter(x, **filter_args.get(x, {}))
            text = file(os.path.join(testdir, testfile)).read().decode('utf-8')
            tokens = list(lx.get_tokens(text))
            roundtext = ''.join([t[1] for t in tokens])
            if x not in ('whitespace', 'keywordcase'):
                # these filters change the text
                self.assertEquals(roundtext, text,
                                  "lexer roundtrip with %s filter failed" % x)

    def test_raiseonerror(self):
        lx = lexers.PythonLexer()
        lx.add_filter('raiseonerror', excclass=RuntimeError)
        self.assertRaises(RuntimeError, list, lx.get_tokens('$'))

    def test_whitespace(self):
        lx = lexers.PythonLexer()
        lx.add_filter('whitespace', spaces='%')
        text = file(os.path.join(testdir, testfile)).read().decode('utf-8')
        lxtext = ''.join([t[1] for t in list(lx.get_tokens(text))])
        self.failIf(' ' in lxtext)

    def test_keywordcase(self):
        lx = lexers.PythonLexer()
        lx.add_filter('keywordcase', case='capitalize')
        text = file(os.path.join(testdir, testfile)).read().decode('utf-8')
        lxtext = ''.join([t[1] for t in list(lx.get_tokens(text))])
        self.assert_('Def' in lxtext and 'Class' in lxtext)


class FormattersTest(unittest.TestCase):

    def test_public_api(self):
        a = self.assert_
        ae = self.assertEquals
        ts = list(lexers.PythonLexer().get_tokens("def f(): pass"))
        out = StringIO.StringIO()
        # test that every formatter class has the correct public API
        for formatter, info in formatters.FORMATTERS.iteritems():
            a(len(info) == 4)
            a(info[0], "missing formatter name") # name
            a(info[1], "missing formatter aliases") # aliases
            a(info[3], "missing formatter docstring") # doc

            try:
                inst = formatter(opt1="val1")
            except (ImportError, FontNotFound):
                continue
            inst.get_style_defs()
            inst.format(ts, out)

    def test_encodings(self):
        from pygments.formatters import HtmlFormatter

        # unicode output
        fmt = HtmlFormatter()
        tokens = [(Text, u"ä")]
        out = format(tokens, fmt)
        self.assert_(type(out) is unicode)
        self.assert_(u"ä" in out)

        # encoding option
        fmt = HtmlFormatter(encoding="latin1")
        tokens = [(Text, u"ä")]
        self.assert_(u"ä".encode("latin1") in format(tokens, fmt))

        # encoding and outencoding option
        fmt = HtmlFormatter(encoding="latin1", outencoding="utf8")
        tokens = [(Text, u"ä")]
        self.assert_(u"ä".encode("utf8") in format(tokens, fmt))

    def test_styles(self):
        from pygments.formatters import HtmlFormatter
        fmt = HtmlFormatter(style="pastie")

    def test_unicode_handling(self):
        # test that the formatter supports encoding and Unicode
        tokens = list(lexers.PythonLexer(encoding='utf-8').get_tokens("def f(): 'ä'"))
        for formatter, info in formatters.FORMATTERS.iteritems():
            try:
                inst = formatter(encoding=None)
            except (ImportError, FontNotFound):
                # some dependency or font not installed
                continue
            out = format(tokens, inst)
            if formatter.unicodeoutput:
                self.assert_(type(out) is unicode)

            inst = formatter(encoding='utf-8')
            out = format(tokens, inst)
            self.assert_(type(out) is str)
            # Cannot test for encoding, since formatters may have to escape
            # non-ASCII characters.

    def test_get_formatters(self):
        a = self.assert_
        ae = self.assertEquals
        # test that the formatters functions work
        x = formatters.get_formatter_by_name("html", opt="val")
        a(isinstance(x, formatters.HtmlFormatter))
        ae(x.options["opt"], "val")

        x = formatters.get_formatter_for_filename("a.html", opt="val")
        a(isinstance(x, formatters.HtmlFormatter))
        ae(x.options["opt"], "val")
