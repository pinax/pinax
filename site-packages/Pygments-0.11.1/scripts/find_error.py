#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Lexing error finder
    ~~~~~~~~~~~~~~~~~~~

    For the source files given on the command line, display
    the text where Error tokens are being generated, along
    with some context.

    :copyright: 2006-2007 by Tim Hatch <tim@timhatch.com>.
    :license: BSD, see LICENSE for more details.
"""

import sys, os

try:
    import pygments
except ImportError:
    # try parent path
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from pygments import highlight
from pygments.lexers import get_lexer_for_filename, get_lexer_by_name
from pygments.token import Error

def main(fn):
    try:
        lx = get_lexer_for_filename(fn)
    except ValueError:
        try:
            name, rest = fn.split("_", 1)
            lx = get_lexer_by_name(name)
        except ValueError:
            raise AssertionError('no lexer found for file %r' % fn)
    text = file(fn, 'U').read()
    text = text.strip('\n') + '\n'
    text = text.decode('latin1')
    ntext = []
    for type, val in lx.get_tokens(text):
        if type == Error:
            print "Error parsing", fn
            print "\n".join(['   ' + repr(x) for x in ntext[-num:]])
            print `val` + "<<<"
            return
        ntext.append((type,val))


num = 10

if __name__ == "__main__":
    if sys.argv[1][:2] == '-n':
        num = int(sys.argv[1][2:])
        del sys.argv[1]
    for f in sys.argv[1:]:
        main(f)
