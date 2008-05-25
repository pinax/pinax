#!/usr/bin/env python

"""Tests for yadis.discover.

@todo: Now that yadis.discover uses urljr.fetchers, we should be able to do
   tests with a mock fetcher instead of spawning threads with BaseHTTPServer.
"""

import unittest
import urlparse
import re
import types

from openid.yadis.discover import discover, DiscoveryFailure

from openid import fetchers

import discoverdata

status_header_re = re.compile(r'Status: (\d+) .*?$', re.MULTILINE)

four04_pat = """\
Content-Type: text/plain

No such file %s
"""

class QuitServer(Exception): pass

def mkResponse(data):
    status_mo = status_header_re.match(data)
    headers_str, body = data.split('\n\n', 1)
    headers = {}
    for line in headers_str.split('\n'):
        k, v = line.split(':', 1)
        k = k.strip().lower()
        v = v.strip()
        headers[k] = v
    status = int(status_mo.group(1))
    return fetchers.HTTPResponse(status=status,
                                 headers=headers,
                                 body=body)

class TestFetcher(object):
    def __init__(self, base_url):
        self.base_url = base_url

    def fetch(self, url, headers, body):
        current_url = url
        while True:
            parsed = urlparse.urlparse(current_url)
            path = parsed[2][1:]
            try:
                data = discoverdata.generateSample(path, self.base_url)
            except KeyError:
                return fetchers.HTTPResponse(status=404,
                                             final_url=current_url,
                                             headers={},
                                             body='')

            response = mkResponse(data)
            if response.status in [301, 302, 303, 307]:
                current_url = response.headers['location']
            else:
                response.final_url = current_url
                return response

class TestSecondGet(unittest.TestCase):
    class MockFetcher(object):
        def __init__(self):
            self.count = 0
        def fetch(self, uri, headers=None, body=None):
            self.count += 1
            if self.count == 1:
                headers = {
                    'X-XRDS-Location'.lower(): 'http://unittest/404',
                    }
                return fetchers.HTTPResponse(uri, 200, headers, '')
            else:
                return fetchers.HTTPResponse(uri, 404)

    def setUp(self):
        self.oldfetcher = fetchers.getDefaultFetcher()
        fetchers.setDefaultFetcher(self.MockFetcher())

    def tearDown(self):
        fetchers.setDefaultFetcher(self.oldfetcher)

    def test_404(self):
        uri = "http://something.unittest/"
        self.failUnlessRaises(DiscoveryFailure, discover, uri)


class _TestCase(unittest.TestCase):
    base_url = 'http://invalid.unittest/'

    def __init__(self, input_name, id_name, result_name, success):
        self.input_name = input_name
        self.id_name = id_name
        self.result_name = result_name
        self.success = success
        # Still not quite sure how to best construct these custom tests.
        # Between python2.3 and python2.4, a patch attached to pyunit.sf.net
        # bug #469444 got applied which breaks loadTestsFromModule on this
        # class if it has test_ or runTest methods.  So, kludge to change
        # the method name.
        unittest.TestCase.__init__(self, methodName='runCustomTest')

    def setUp(self):
        fetchers.setDefaultFetcher(TestFetcher(self.base_url),
                                   wrap_exceptions=False)

        self.input_url, self.expected = discoverdata.generateResult(
            self.base_url,
            self.input_name,
            self.id_name,
            self.result_name,
            self.success)

    def tearDown(self):
        fetchers.setDefaultFetcher(None)

    def runCustomTest(self):
        if self.expected is DiscoveryFailure:
            self.failUnlessRaises(DiscoveryFailure,
                                  discover, self.input_url)
        else:
            result = discover(self.input_url)
            self.failUnlessEqual(self.input_url, result.request_uri)

            msg = 'Identity URL mismatch: actual = %r, expected = %r' % (
                result.normalized_uri, self.expected.normalized_uri)
            self.failUnlessEqual(
                self.expected.normalized_uri, result.normalized_uri, msg)

            msg = 'Content mismatch: actual = %r, expected = %r' % (
                result.response_text, self.expected.response_text)
            self.failUnlessEqual(
                self.expected.response_text, result.response_text, msg)

            expected_keys = dir(self.expected)
            expected_keys.sort()
            actual_keys = dir(result)
            actual_keys.sort()
            self.failUnlessEqual(actual_keys, expected_keys)

            for k in dir(self.expected):
                if k.startswith('__') and k.endswith('__'):
                    continue
                exp_v = getattr(self.expected, k)
                if isinstance(exp_v, types.MethodType):
                    continue
                act_v = getattr(result, k)
                assert act_v == exp_v, (k, exp_v, act_v)

    def shortDescription(self):
        try:
            n = self.input_url
        except AttributeError:
            # run before setUp, or if setUp did not complete successfully.
            n = self.input_name
        return "%s (%s)" % (
            n,
            self.__class__.__module__)

def pyUnitTests():
    s = unittest.TestSuite()
    for success, input_name, id_name, result_name in discoverdata.testlist:
        test = _TestCase(input_name, id_name, result_name, success)
        s.addTest(test)

    return s

def test():
    runner = unittest.TextTestRunner()
    return runner.run(loadTests())

if __name__ == '__main__':
    test()
