#!/bin/sh
ls -1 `dirname $0` | grep -v packages.pth | grep -v update.sh > `dirname $0`/packages.pth
cat `dirname $0`/packages.pth
