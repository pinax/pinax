import unittest

from openid.yadis import services
from openid.yadis.discover import DiscoveryFailure, DiscoveryResult


class TestGetServiceEndpoints(unittest.TestCase):
    def setUp(self):
        self.orig_discover = services.discover
        services.discover = self.discover

    def tearDown(self):
        services.discover = self.orig_discover

    def discover(self, input_url):
        result = DiscoveryResult(input_url)
        result.response_text = "This is not XRDS text."
        return result

    def test_catchXRDSError(self):
        self.failUnlessRaises(DiscoveryFailure,
                              services.getServiceEndpoints,
                              "http://example.invalid/sometest")
