#!/usr/bin/env python

import os
import os.path
import sys

if len(sys.argv) == 2:
    top = sys.argv[1]
else:
    top = "."

for root, dirs, files in os.walk(top):
    for filename in files:
        path = os.path.join(root, filename)
        if any(filename.endswith(ending) for ending in [".py", ".html", ".txt", ".css"]):
            tabs = False
            cr = False
            trail = False
            for line_num, line in enumerate(open(path)):
                if "\t" in line:
                    tabs = line_num + 1
                if "\r" in line:
                    cr = line_num + 1
                if line.strip() and line.rstrip() != line.rstrip("\n\r"):
                    trail = line_num + 1
                if tabs and cr and trail: # shortcut out if we all three
                    break
            if tabs:
                print "TABS in", path, "(last %s)" % tabs
            if cr:
                print "CR in", path, "(last %s)" % cr
            if trail:
                print "TRAIL in", path, "(last %s)" % trail
