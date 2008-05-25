#!/usr/bin/env python

import os.path
import urlparse

from yadis.test import test_parsehtml

#### Code for creating static files to test against

manifest_header = """\
# This file contains test cases for embedding YADIS service document
# URLs inside of a HTML document. For each case, the URL to the
# document containing the case and the expected output are listed.
#
# The file format is as follows:
# URL <tab> expected output <newline>
#
# blank lines and lines starting with # should be ignored.
#
# There are two special values for expected output, 'EOF' and
# 'None'. In each of these cases, no url should have been found. In
# the case of 'None', it is possible to stop parsing before the end of
# the file. In the case of 'EOF', the entire file needed to be read to
# know that the URL was not found. It is acceptable to treat these
# cases the same way. The distinction is provided for those who want
# to optimize their parsers.

"""

def writeStaticCases(cases, target_dir):
    """Create a set of test files from the html test case file.

    ([(str, str)], str) -> [(str, str)]
    """
    manifest = []
    test_num = 0
    for expected, markup in cases:
        output_name = 'test-%d.html' % (test_num,)
        output_path = os.path.join(target_dir, output_name)
        output_file = file(output_path, 'w')
        output_file.write(markup)
        output_file.close()
        test_num += 1

        manifest.append((output_name, expected))

    return manifest

def buildManifest(manifest_data, base_url):
    manifest_chunks = [manifest_header]
    for (output_name, expected) in manifest_data:
        url = urlparse.urljoin(base_url, output_name)
        manifest_chunks.append('%s\t%s\n' % (url, expected))

    return ''.join(manifest_chunks)

def buildHTML(base_url, target_dir):
    cases = []
    for (_, _, expected, case) in test_parsehtml.getCases():
        cases.append((expected, case))

    manifest_data = writeStaticCases(cases, target_dir)
    manifest_text = buildManifest(manifest_data, base_url)
    manifest_filename = os.path.join(target_dir, 'manifest.txt')
    manifest_file = file(manifest_filename, 'w')
    manifest_file.write(manifest_text)
    manifest_file.close()
