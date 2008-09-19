#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Source line counter
    ~~~~~~~~~~~~~~~~~~~

    Count the lines of code in pocoo, colubrid and jinja.
    Requires an svn checkout.

    :copyright: 2006-2007 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
from pocoo.utils.path import Path

def main(root, search):
    LOC = 0

    root = Path(root).realpath()
    offset = len(root) + 1

    print '+%s+' % ('=' * 78)
    print '| Lines of Code %s |' % (' ' * 62)
    print '+%s+' % ('=' * 78)

    for folder in search:
        folder = Path(root).joinpath(folder).realpath()
        for fn in folder.walk():
            if fn.endswith('.py') or fn.endswith('.js'):
                try:
                    fp = file(fn)
                    lines = sum(1 for l in fp.read().splitlines() if l.strip())
                except:
                    print '%-70sskipped' % fn
                else:
                    LOC += lines
                    print '| %-68s %7d |' % (fn[offset:], lines)
                fp.close()

    print '+%s+' % ('-' * 78)
    print '| Total Lines of Code: %55d |' % LOC
    print '+%s+' % ('-' * 78)

if __name__ == '__main__':
    main('../../../', [
        'pocoo/trunk',
        'colubrid/trunk',
        'jinja/trunk'
    ])
