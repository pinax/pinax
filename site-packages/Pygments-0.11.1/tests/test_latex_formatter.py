# -*- coding: utf-8 -*-
"""
    Pygments LaTeX formatter tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2006-2007 by Georg Brandl.
    :license: BSD, see LICENSE for more details.
"""

import os
import unittest
import tempfile

from pygments.formatters import LatexFormatter
from pygments.lexers import PythonLexer


class LatexFormatterTest(unittest.TestCase):

    def test_valid_output(self):
        tokensource = list(PythonLexer().get_tokens(file(
            os.path.join(testdir, testfile)).read()))
        fmt = LatexFormatter(full=True)

        handle, pathname = tempfile.mkstemp('.tex')
        # place all output files in /tmp too
        old_wd = os.getcwd()
        os.chdir(os.path.dirname(pathname))
        tfile = os.fdopen(handle, 'w+b')
        fmt.format(tokensource, tfile)
        tfile.close()
        try:
            try:
                import subprocess
                ret = subprocess.Popen(['latex', '-interaction=nonstopmode', pathname],
                                       stdout=subprocess.PIPE).wait()
            except ImportError:
                # Python 2.3 - no subprocess module
                ret = os.popen('latex -interaction=nonstopmode "%s"' % pathname).close()
                if ret == 32512: raise OSError  # not found
        except OSError:
            # latex not available
            pass
        else:
            self.failIf(ret, 'latex run reported errors')

        os.unlink(pathname)
        os.chdir(old_wd)
