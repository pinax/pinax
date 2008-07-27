import unittest
import urllib2

from yadis.discover import discover

def parseManifest(lines):
    cases = []
    for line in lines:
        if line.startswith('#') or not line.strip():
            continue

        # remove newline
        assert line[-1] == '\n'
        line = line[:-1]

        # split fields
        parts = line.split('\t')
        assert len(parts) == 3

        cases.append(tuple(parts))

    return cases

class DiscoverTestCase(unittest.TestCase):
    def __init__(self, input_url, normalized_url, xrds_url):
        unittest.TestCase.__init__(self)
        self.input_url = input_url
        self.normalized_url = normalized_url
        self.xrds_url = xrds_url

    def runTest(self):
        normalized_url, content = discover(self.input_url)

        msg = 'Identity URL mismatch: actual = %r, expected = %r' % (
            normalized_url, self.normalized_url)
        self.failUnlessEqual(self.normalized_url, normalized_url, msg)

        resp = urllib2.urlopen(self.xrds_url)
        expected_content = resp.read()
        resp.close()

        msg = 'XRDS content mismatch: actual = %r, expected = %r' % (
            content, expected_content)
        self.failUnlessEqual(expected_content, content, msg)

    def shortDescription(self):
        return "%s (%s)" % (self.input_url, self.__class__.__module__)

def mkSuite(parsed):
    test_cases = [DiscoverTestCase(*t) for t in parsed]
    return unittest.TestSuite(test_cases)

def mkSuiteFromURL(manifest_url):
    req = urllib2.urlopen(manifest_url)
    parsed = parseManifest(req)
    return mkSuite(parsed)

def test(url):
    suite = mkSuiteFromURL(url)
    runner = unittest.TextTestRunner()
    return runner.run(suite)

if __name__ == '__main__':
    import sys
    test(sys.argv[1])
