# -*- coding: utf-8 -*-
"""
    Pygments HTML formatter tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2006-2007 by Georg Brandl.
    :license: BSD, see LICENSE for more details.
"""

import os
import re
import unittest
import StringIO
import tempfile
from os.path import join, dirname, isfile

from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter, NullFormatter
from pygments.formatters.html import escape_html

tokensource = list(PythonLexer().get_tokens(file(
    os.path.join(testdir, testfile)).read()))

class HtmlFormatterTest(unittest.TestCase):
    def test_correct_output(self):
        hfmt = HtmlFormatter(nowrap=True)
        houtfile = StringIO.StringIO()
        hfmt.format(tokensource, houtfile)

        nfmt = NullFormatter()
        noutfile = StringIO.StringIO()
        nfmt.format(tokensource, noutfile)

        stripped_html = re.sub('<.*?>', '', houtfile.getvalue())
        escaped_text = escape_html(noutfile.getvalue())
        self.assertEquals(stripped_html, escaped_text)

    def test_external_css(self):
        # test correct behavior
        # CSS should be in /tmp directory
        fmt1 = HtmlFormatter(full=True, cssfile='fmt1.css')
        # CSS should be in testdir (testdir is absolute)
        fmt2 = HtmlFormatter(full=True, cssfile=join(testdir, 'fmt2.css'))
        tfile = tempfile.NamedTemporaryFile(suffix='.html')
        fmt1.format(tokensource, tfile)
        try:
            fmt2.format(tokensource, tfile)
            self.assert_(isfile(join(testdir, 'fmt2.css')))
        except IOError:
            # test directory not writable
            pass
        tfile.close()

        self.assert_(isfile(join(dirname(tfile.name), 'fmt1.css')))
        os.unlink(join(dirname(tfile.name), 'fmt1.css'))
        try:
            os.unlink(join(testdir, 'fmt2.css'))
        except OSError:
            pass

    def test_all_options(self):
        for optdict in [dict(nowrap=True),
                        dict(linenos=True),
                        dict(linenos=True, full=True),
                        dict(linenos=True, full=True, noclasses=True)]:

            outfile = StringIO.StringIO()
            fmt = HtmlFormatter(**optdict)
            fmt.format(tokensource, outfile)

    def test_valid_output(self):
        # test all available wrappers
        fmt = HtmlFormatter(full=True, linenos=True, noclasses=True)

        handle, pathname = tempfile.mkstemp('.html')
        tfile = os.fdopen(handle, 'w+b')
        fmt.format(tokensource, tfile)
        tfile.close()
        catname = os.path.join(testdir, 'dtds', 'HTML4.soc')
        try:
            try:
                import subprocess
                ret = subprocess.Popen(['nsgmls', '-s', '-c', catname, pathname],
                                       stdout=subprocess.PIPE).wait()
            except ImportError:
                # Python 2.3 - no subprocess module
                ret = os.popen('nsgmls -s -c "%s" "%s"' % (catname, pathname)).close()
                if ret == 32512: raise OSError  # not found
        except OSError:
            # latex not available
            pass
        else:
            self.failIf(ret, 'nsgmls run reported errors')

        os.unlink(pathname)

    def test_get_style_defs(self):
        fmt = HtmlFormatter()
        sd = fmt.get_style_defs()
        self.assert_(sd.startswith('.'))

        fmt = HtmlFormatter(cssclass='foo')
        sd = fmt.get_style_defs()
        self.assert_(sd.startswith('.foo'))
        sd = fmt.get_style_defs('.bar')
        self.assert_(sd.startswith('.bar'))
        sd = fmt.get_style_defs(['.bar', '.baz'])
        fl = sd.splitlines()[0]
        self.assert_('.bar' in fl and '.baz' in fl)
