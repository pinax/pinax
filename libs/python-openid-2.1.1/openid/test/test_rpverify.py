"""Unit tests for verification of return_to URLs for a realm
"""

__all__ = ['TestBuildDiscoveryURL']

from openid.yadis.discover import DiscoveryResult, DiscoveryFailure
from openid.yadis import services
from openid.server import trustroot
from openid.test.support import CatchLogs
import unittest

# Too many methods does not apply to unit test objects
#pylint:disable-msg=R0904
class TestBuildDiscoveryURL(unittest.TestCase):
    """Tests for building the discovery URL from a realm and a
    return_to URL
    """

    def failUnlessDiscoURL(self, realm, expected_discovery_url):
        """Build a discovery URL out of the realm and a return_to and
        make sure that it matches the expected discovery URL
        """
        realm_obj = trustroot.TrustRoot.parse(realm)
        actual_discovery_url = realm_obj.buildDiscoveryURL()
        self.failUnlessEqual(expected_discovery_url, actual_discovery_url)

    def test_trivial(self):
        """There is no wildcard and the realm is the same as the return_to URL
        """
        self.failUnlessDiscoURL('http://example.com/foo',
                                'http://example.com/foo')

    def test_wildcard(self):
        """There is a wildcard
        """
        self.failUnlessDiscoURL('http://*.example.com/foo',
                                'http://www.example.com/foo')

class TestExtractReturnToURLs(unittest.TestCase):
    disco_url = 'http://example.com/'

    def setUp(self):
        self.original_discover = services.discover
        services.discover = self.mockDiscover
        self.data = None

    def tearDown(self):
        services.discover = self.original_discover

    def mockDiscover(self, uri):
        result = DiscoveryResult(uri)
        result.response_text = self.data
        result.normalized_uri = uri
        return result

    def failUnlessFileHasReturnURLs(self, filename, expected_return_urls):
        self.failUnlessXRDSHasReturnURLs(file(filename).read(),
                                         expected_return_urls)

    def failUnlessXRDSHasReturnURLs(self, data, expected_return_urls):
        self.data = data
        actual_return_urls = list(trustroot.getAllowedReturnURLs(
            self.disco_url))

        self.failUnlessEqual(expected_return_urls, actual_return_urls)

    def failUnlessDiscoveryFailure(self, text):
        self.data = text
        self.failUnlessRaises(
            DiscoveryFailure, trustroot.getAllowedReturnURLs, self.disco_url)

    def test_empty(self):
        self.failUnlessDiscoveryFailure('')

    def test_badXML(self):
        self.failUnlessDiscoveryFailure('>')

    def test_noEntries(self):
        self.failUnlessXRDSHasReturnURLs('''\
<?xml version="1.0" encoding="UTF-8"?>
<xrds:XRDS xmlns:xrds="xri://$xrds"
           xmlns="xri://$xrd*($v*2.0)"
           >
  <XRD>
  </XRD>
</xrds:XRDS>
''', [])

    def test_noReturnToEntries(self):
        self.failUnlessXRDSHasReturnURLs('''\
<?xml version="1.0" encoding="UTF-8"?>
<xrds:XRDS xmlns:xrds="xri://$xrds"
           xmlns="xri://$xrd*($v*2.0)"
           >
  <XRD>
    <Service priority="10">
      <Type>http://specs.openid.net/auth/2.0/server</Type>
      <URI>http://www.myopenid.com/server</URI>
    </Service>
  </XRD>
</xrds:XRDS>
''', [])

    def test_oneEntry(self):
        self.failUnlessXRDSHasReturnURLs('''\
<?xml version="1.0" encoding="UTF-8"?>
<xrds:XRDS xmlns:xrds="xri://$xrds"
           xmlns="xri://$xrd*($v*2.0)"
           >
  <XRD>
    <Service>
      <Type>http://specs.openid.net/auth/2.0/return_to</Type>
      <URI>http://rp.example.com/return</URI>
    </Service>
  </XRD>
</xrds:XRDS>
''', ['http://rp.example.com/return'])

    def test_twoEntries(self):
        self.failUnlessXRDSHasReturnURLs('''\
<?xml version="1.0" encoding="UTF-8"?>
<xrds:XRDS xmlns:xrds="xri://$xrds"
           xmlns="xri://$xrd*($v*2.0)"
           >
  <XRD>
    <Service priority="0">
      <Type>http://specs.openid.net/auth/2.0/return_to</Type>
      <URI>http://rp.example.com/return</URI>
    </Service>
    <Service priority="1">
      <Type>http://specs.openid.net/auth/2.0/return_to</Type>
      <URI>http://other.rp.example.com/return</URI>
    </Service>
  </XRD>
</xrds:XRDS>
''', ['http://rp.example.com/return',
      'http://other.rp.example.com/return'])

    def test_twoEntries_withOther(self):
        self.failUnlessXRDSHasReturnURLs('''\
<?xml version="1.0" encoding="UTF-8"?>
<xrds:XRDS xmlns:xrds="xri://$xrds"
           xmlns="xri://$xrd*($v*2.0)"
           >
  <XRD>
    <Service priority="0">
      <Type>http://specs.openid.net/auth/2.0/return_to</Type>
      <URI>http://rp.example.com/return</URI>
    </Service>
    <Service priority="1">
      <Type>http://specs.openid.net/auth/2.0/return_to</Type>
      <URI>http://other.rp.example.com/return</URI>
    </Service>
    <Service priority="0">
      <Type>http://example.com/LOLCATS</Type>
      <URI>http://example.com/invisible+uri</URI>
    </Service>
  </XRD>
</xrds:XRDS>
''', ['http://rp.example.com/return',
      'http://other.rp.example.com/return'])



class TestReturnToMatches(unittest.TestCase):
    def test_noEntries(self):
        self.failIf(trustroot.returnToMatches([], 'anything'))

    def test_exactMatch(self):
        r = 'http://example.com/return.to'
        self.failUnless(trustroot.returnToMatches([r], r))

    def test_garbageMatch(self):
        r = 'http://example.com/return.to'
        self.failUnless(trustroot.returnToMatches(
            ['This is not a URL at all. In fact, it has characters, '
             'like "<" that are not allowed in URLs',
             r],
            r))

    def test_descendant(self):
        r = 'http://example.com/return.to'
        self.failUnless(trustroot.returnToMatches(
            [r],
            'http://example.com/return.to/user:joe'))

    def test_wildcard(self):
        self.failIf(trustroot.returnToMatches(
            ['http://*.example.com/return.to'],
            'http://example.com/return.to'))

    def test_noMatch(self):
        r = 'http://example.com/return.to'
        self.failIf(trustroot.returnToMatches(
            [r],
            'http://example.com/xss_exploit'))

class TestVerifyReturnTo(unittest.TestCase, CatchLogs):

    def setUp(self):
        CatchLogs.setUp(self)

    def tearDown(self):
        CatchLogs.tearDown(self)
    
    def test_bogusRealm(self):
        self.failIf(trustroot.verifyReturnTo('', 'http://example.com/'))

    def test_verifyWithDiscoveryCalled(self):
        realm = 'http://*.example.com/'
        return_to = 'http://www.example.com/foo'

        def vrfy(disco_url):
            self.failUnlessEqual('http://www.example.com/', disco_url)
            return [return_to]

        self.failUnless(
            trustroot.verifyReturnTo(realm, return_to, _vrfy=vrfy))
        self.failUnlessLogEmpty()

    def test_verifyFailWithDiscoveryCalled(self):
        realm = 'http://*.example.com/'
        return_to = 'http://www.example.com/foo'

        def vrfy(disco_url):
            self.failUnlessEqual('http://www.example.com/', disco_url)
            return ['http://something-else.invalid/']

        self.failIf(
            trustroot.verifyReturnTo(realm, return_to, _vrfy=vrfy))
        self.failUnlessLogMatches("Failed to validate return_to")

    def test_verifyFailIfDiscoveryRedirects(self):
        realm = 'http://*.example.com/'
        return_to = 'http://www.example.com/foo'

        def vrfy(disco_url):
            raise trustroot.RealmVerificationRedirected(
                disco_url, "http://redirected.invalid")

        self.failIf(
            trustroot.verifyReturnTo(realm, return_to, _vrfy=vrfy))
        self.failUnlessLogMatches("Attempting to verify")

if __name__ == '__main__':
    unittest.main()
