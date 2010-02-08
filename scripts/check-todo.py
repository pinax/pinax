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
            marked = []
            for line_num, line in enumerate(open(path)):
                if "@@@" in line or "TODO" in line or "FIXME" in line:
                    marked.append(line_num + 1)
            if marked:
                print "%s : %s" % (path, marked)
