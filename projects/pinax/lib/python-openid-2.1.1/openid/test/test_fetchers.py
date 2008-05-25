import warnings
import unittest
import sys
import urllib2
import socket

from openid import fetchers

# XXX: make these separate test cases

def failUnlessResponseExpected(expected, actual):
    assert expected.final_url == actual.final_url, (
        "%r != %r" % (expected.final_url, actual.final_url))
    assert expected.status == actual.status
    assert expected.body == actual.body
    got_headers = dict(actual.headers)
    del got_headers['date']
    del got_headers['server']
    for k, v in expected.headers.iteritems():
        assert got_headers[k] == v, (k, v, got_headers[k])

def test_fetcher(fetcher, exc, server):
    def geturl(path):
        return 'http://%s:%s%s' % (socket.getfqdn(server.server_name),
                                   server.socket.getsockname()[1],
                                   path)

    expected_headers = {'content-type':'text/plain'}

    def plain(path, code):
        path = '/' + path
        expected = fetchers.HTTPResponse(
            geturl(path), code, expected_headers, path)
        return (path, expected)

    expect_success = fetchers.HTTPResponse(
        geturl('/success'), 200, expected_headers, '/success')
    cases = [
        ('/success', expect_success),
        ('/301redirect', expect_success),
        ('/302redirect', expect_success),
        ('/303redirect', expect_success),
        ('/307redirect', expect_success),
        plain('notfound', 404),
        plain('badreq', 400),
        plain('forbidden', 403),
        plain('error', 500),
        plain('server_error', 503),
        ]

    for path, expected in cases:
        fetch_url = geturl(path)
        try:
            actual = fetcher.fetch(fetch_url)
        except (SystemExit, KeyboardInterrupt):
            pass
        except:
            print fetcher, fetch_url
            raise
        else:
            failUnlessResponseExpected(expected, actual)

    for err_url in [geturl('/closed'),
                    'http://invalid.janrain.com/',
                    'not:a/url',
                    'ftp://janrain.com/pub/']:
        try:
            result = fetcher.fetch(err_url)
        except (KeyboardInterrupt, SystemExit):
            raise
        except fetchers.HTTPError, why:
            # This is raised by the Curl fetcher for bad cases
            # detected by the fetchers module, but it's a subclass of
            # HTTPFetchingError, so we have to catch it explicitly.
            assert exc
        except fetchers.HTTPFetchingError, why:
            assert not exc, (fetcher, exc, server)
        except:
            assert exc
        else:
            assert False, 'An exception was expected for %r (%r)' % (fetcher, result)

def run_fetcher_tests(server):
    exc_fetchers = []
    for klass, library_name in [
        (fetchers.Urllib2Fetcher, 'urllib2'),
        (fetchers.CurlHTTPFetcher, 'pycurl'),
        (fetchers.HTTPLib2Fetcher, 'httplib2'),
        ]:
        try:
            exc_fetchers.append(klass())
        except RuntimeError, why:
            if why[0].startswith('Cannot find %s library' % (library_name,)):
                try:
                    __import__(library_name)
                except ImportError:
                    warnings.warn(
                        'Skipping tests for %r fetcher because '
                        'the library did not import.' % (library_name,))
                    pass
                else:
                    assert False, ('%s present but not detected' % (library_name,))
            else:
                raise

    non_exc_fetchers = []
    for f in exc_fetchers:
        non_exc_fetchers.append(fetchers.ExceptionWrappingFetcher(f))

    for f in exc_fetchers:
        test_fetcher(f, True, server)

    for f in non_exc_fetchers:
        test_fetcher(f, False, server)

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

class FetcherTestHandler(BaseHTTPRequestHandler):
    cases = {
        '/success':(200, None),
        '/301redirect':(301, '/success'),
        '/302redirect':(302, '/success'),
        '/303redirect':(303, '/success'),
        '/307redirect':(307, '/success'),
        '/notfound':(404, None),
        '/badreq':(400, None),
        '/forbidden':(403, None),
        '/error':(500, None),
        '/server_error':(503, None),
        }

    def log_request(self, *args):
        pass

    def do_GET(self):
        if self.path == '/closed':
            self.wfile.close()
        else:
            try:
                http_code, location = self.cases[self.path]
            except KeyError:
                self.errorResponse('Bad path')
            else:
                extra_headers = [('Content-type', 'text/plain')]
                if location is not None:
                    host, port = self.server.server_address
                    base = ('http://%s:%s' % (socket.getfqdn(host), port,))
                    location = base + location
                    extra_headers.append(('Location', location))
                self._respond(http_code, extra_headers, self.path)

    def do_POST(self):
        try:
            http_code, extra_headers = self.cases[self.path]
        except KeyError:
            self.errorResponse('Bad path')
        else:
            if http_code in [301, 302, 303, 307]:
                self.errorResponse()
            else:
                content_type = self.headers.get('content-type', 'text/plain')
                extra_headers.append(('Content-type', content_type))
                content_length = int(self.headers.get('Content-length', '-1'))
                body = self.rfile.read(content_length)
                self._respond(http_code, extra_headers, body)

    def errorResponse(self, message=None):
        req = [
            ('HTTP method', self.command),
            ('path', self.path),
            ]
        if message:
            req.append(('message', message))

        body_parts = ['Bad request:\r\n']
        for k, v in req:
            body_parts.append(' %s: %s\r\n' % (k, v))
        body = ''.join(body_parts)
        self._respond(400, [('Content-type', 'text/plain')], body)

    def _respond(self, http_code, extra_headers, body):
        self.send_response(http_code)
        for k, v in extra_headers:
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)
        self.wfile.close()

    def finish(self):
        if not self.wfile.closed:
            self.wfile.flush()
        self.wfile.close()
        self.rfile.close()

def test():
    import socket
    host = socket.getfqdn('127.0.0.1')
    # When I use port 0 here, it works for the first fetch and the
    # next one gets connection refused.  Bummer.  So instead, pick a
    # port that's *probably* not in use.
    import os
    port = (os.getpid() % 31000) + 1024

    server = HTTPServer((host, port), FetcherTestHandler)

    import threading
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.setDaemon(True)
    server_thread.start()

    run_fetcher_tests(server)

class FakeFetcher(object):
    sentinel = object()

    def fetch(self, *args, **kwargs):
        return self.sentinel

class DefaultFetcherTest(unittest.TestCase):
    def setUp(self):
        """reset the default fetcher to None"""
        fetchers.setDefaultFetcher(None)

    def tearDown(self):
        """reset the default fetcher to None"""
        fetchers.setDefaultFetcher(None)

    def test_getDefaultNotNone(self):
        """Make sure that None is never returned as a default fetcher"""
        self.failUnless(fetchers.getDefaultFetcher() is not None)
        fetchers.setDefaultFetcher(None)
        self.failUnless(fetchers.getDefaultFetcher() is not None)

    def test_setDefault(self):
        """Make sure the getDefaultFetcher returns the object set for
        setDefaultFetcher"""
        sentinel = object()
        fetchers.setDefaultFetcher(sentinel, wrap_exceptions=False)
        self.failUnless(fetchers.getDefaultFetcher() is sentinel)

    def test_callFetch(self):
        """Make sure that fetchers.fetch() uses the default fetcher
        instance that was set."""
        fetchers.setDefaultFetcher(FakeFetcher())
        actual = fetchers.fetch('bad://url')
        self.failUnless(actual is FakeFetcher.sentinel)

    def test_wrappedByDefault(self):
        """Make sure that the default fetcher instance wraps
        exceptions by default"""
        default_fetcher = fetchers.getDefaultFetcher()
        self.failUnless(isinstance(default_fetcher,
                                   fetchers.ExceptionWrappingFetcher),
                        default_fetcher)

        self.failUnlessRaises(fetchers.HTTPFetchingError,
                              fetchers.fetch, 'http://invalid.janrain.com/')

    def test_notWrapped(self):
        """Make sure that if we set a non-wrapped fetcher as default,
        it will not wrap exceptions."""
        # A fetcher that will raise an exception when it encounters a
        # host that will not resolve
        fetcher = fetchers.Urllib2Fetcher()
        fetchers.setDefaultFetcher(fetcher, wrap_exceptions=False)

        self.failIf(isinstance(fetchers.getDefaultFetcher(),
                               fetchers.ExceptionWrappingFetcher))

        try:
            fetchers.fetch('http://invalid.janrain.com/')
        except fetchers.HTTPFetchingError:
            self.fail('Should not be wrapping exception')
        except:
            exc = sys.exc_info()[1]
            self.failUnless(isinstance(exc, urllib2.URLError), exc)
            pass
        else:
            self.fail('Should have raised an exception')

def pyUnitTests():
    case1 = unittest.FunctionTestCase(test)
    loadTests = unittest.defaultTestLoader.loadTestsFromTestCase
    case2 = loadTests(DefaultFetcherTest)
    return unittest.TestSuite([case1, case2])
