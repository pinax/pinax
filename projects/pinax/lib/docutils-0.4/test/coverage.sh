#!/bin/bash

# Author: Felix Wiemann
# Contact: Felix_Wiemann@ososo.de
# Revision: $Revision: 3603 $
# Date: $Date: 2005-06-27 14:47:29 +0200 (Mon, 27 Jun 2005) $
# Copyright: This script has been placed in the public domain.

set -e
proj="${PWD##*/}"
if test "$proj" == test; then
    cd ..
    proj="${PWD##*/}"
fi
if test "$1"; then
    proj="$1"
fi
echo "Performing code coverage test for project \"$proj\"..."
echo
echo "Please be patient; coverage tracking slows test execution down by more"
echo "than factor 10."
echo
cd test
rm -rf cover
mkdir -p cover
python -u -m trace --count --coverdir=cover --missing alltests.py
cd ..
echo
echo
echo Uncovered lines
echo ===============
echo
(
    find "$proj" -name \*.py | while read i; do
        i="${i%.py}"
        test -f test/cover/"${i//\//.}".cover -o "${i##*/}" == Template || echo "${i//\//.}" "`cat "$i.py" | wc -l`"
    done
    cd test/cover
    find . \( -name . -o ! -name "$proj".\* -exec rm {} \; \)
    for i in *.cover; do
        sed 's/^>>>>>> \(.*"""\)/       \1/' < "$i" > "${i%.cover}"
        rm "$i"
    done
    for i in *; do echo -n "$i "; grep -c '^>>>>>> ' "$i" || true; done
) | grep -v ' 0$' | sort -nk 2
