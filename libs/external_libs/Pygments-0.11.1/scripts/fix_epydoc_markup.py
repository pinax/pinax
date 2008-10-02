#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    fix_epydoc_tables
    ~~~~~~~~~~~~~~~~~

    Fix epydoc "summary" tables.

    :copyright: 2006-2007 by Georg Brandl.
    :license: GNU GPL, see LICENSE for more details.
"""

import sys, os
from os.path import join

path = sys.argv[1]

for fn in os.listdir(path):
    fn = join(path, fn)
    if not fn.endswith(".html"):
        continue

    ll = list(file(fn))
    c = False
    d = False
    n = False

    for i, l in enumerate(ll):
        if "<!-- ===" in l:
            d = ("DETAILS" in l)
            continue
        if l.startswith('<table class="summary"') and d:
            ll[i] = '<table class="detsummary"' + l[len('<table class="summary"'):]
            c = True
            continue
        if l.startswith('<table class="navbar"'):
            if not n:
                n = True
            else:
                ll[i] = '<div style="height: 20px">&nbsp;</div>\n' + l
                c = True

    if c:
        f = file(fn, "w")
        f.write(''.join(ll))
        f.close()
