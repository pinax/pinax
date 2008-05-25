
from unittest import TestCase
from openid.yadis import xrires

class ProxyQueryTestCase(TestCase):
    def setUp(self):
        self.proxy_url = 'http://xri.example.com/'
        self.proxy = xrires.ProxyResolver(self.proxy_url)
        self.servicetype = 'xri://+i-service*(+forwarding)*($v*1.0)'
        self.servicetype_enc = 'xri%3A%2F%2F%2Bi-service%2A%28%2Bforwarding%29%2A%28%24v%2A1.0%29'


    def test_proxy_url(self):
        st = self.servicetype
        ste = self.servicetype_enc
        args_esc = "_xrd_r=application%2Fxrds%2Bxml&_xrd_t=" + ste
        pqu = self.proxy.queryURL
        h = self.proxy_url
        self.failUnlessEqual(h + '=foo?' + args_esc, pqu('=foo', st))
        self.failUnlessEqual(h + '=foo/bar?baz&' + args_esc,
                             pqu('=foo/bar?baz', st))
        self.failUnlessEqual(h + '=foo/bar?baz=quux&' + args_esc,
                             pqu('=foo/bar?baz=quux', st))
        self.failUnlessEqual(h + '=foo/bar?mi=fa&so=la&' + args_esc,
                             pqu('=foo/bar?mi=fa&so=la', st))

        # With no service endpoint selection.
        args_esc = "_xrd_r=application%2Fxrds%2Bxml%3Bsep%3Dfalse"
        self.failUnlessEqual(h + '=foo?' + args_esc, pqu('=foo', None))


    def test_proxy_url_qmarks(self):
        st = self.servicetype
        ste = self.servicetype_enc
        args_esc = "_xrd_r=application%2Fxrds%2Bxml&_xrd_t=" + ste
        pqu = self.proxy.queryURL
        h = self.proxy_url
        self.failUnlessEqual(h + '=foo/bar??' + args_esc, pqu('=foo/bar?', st))
        self.failUnlessEqual(h + '=foo/bar????' + args_esc,
                             pqu('=foo/bar???', st))
