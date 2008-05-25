#!/usr/bin/env python
import os.path
import urlparse

from openid.test import discoverdata

manifest_header = """\
# This file contains test cases for doing YADIS identity URL and
# service discovery. For each case, there are three URLs. The first
# URL is the user input. The second is the identity URL and the third
# is the URL from which the XRDS document should be read.
#
# The file format is as follows:
# User URL <tab> Identity URL <tab> XRDS URL <newline>
#
# blank lines and lines starting with # should be ignored.
#
# To use this test:
#
# 1. Run your discovery routine on the User URL.
#
# 2. Compare the identity URL returned by the discovery routine to the
#    identity URL on that line of the file. It must be an EXACT match.
#
# 3. Do a regular HTTP GET on the XRDS URL. Compare the content that
#    was returned by your discovery routine with the content returned
#    from that URL. It should also be an exact match.

"""

def buildDiscover(base_url, out_dir):
    """Convert all files in a directory to apache mod_asis files in
    another directory."""
    test_data = discoverdata.readTests(discoverdata.default_test_file)

    def writeTestFile(test_name):
        template = test_data[test_name]

        data = discoverdata.fillTemplate(
            test_name, template, base_url, discoverdata.example_xrds)

        out_file_name = os.path.join(out_dir, test_name)
        out_file = file(out_file_name, 'w')
        out_file.write(data)

    manifest = [manifest_header]
    for success, input_name, id_name, result_name in discoverdata.testlist:
        if not success:
            continue
        writeTestFile(input_name)

        input_url = urlparse.urljoin(base_url, input_name)
        id_url = urlparse.urljoin(base_url, id_name)
        result_url = urlparse.urljoin(base_url, result_name)

        manifest.append('\t'.join((input_url, id_url, result_url)))
        manifest.append('\n')

    manifest_file_name = os.path.join(out_dir, 'manifest.txt')
    manifest_file = file(manifest_file_name, 'w')
    for chunk in manifest:
        manifest_file.write(chunk)
    manifest_file.close()

if __name__ == '__main__':
    import sys
    buildDiscover(*sys.argv[1:])
