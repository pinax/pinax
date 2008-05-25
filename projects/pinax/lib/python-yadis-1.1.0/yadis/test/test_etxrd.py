import unittest
from yadis import services, etxrd, xri
import os.path

def sibpath(one, other, make_absolute=True):
    if os.path.isabs(other):
        return other
    p = os.path.join(os.path.dirname(one), other)
    if make_absolute:
        p = os.path.abspath(p)
    return p


XRD_FILE = sibpath(__file__, os.path.join("data", "test1-xrd.xml"))
NOXRDS_FILE = sibpath(__file__, os.path.join("data", "not-xrds.xml"))
NOXRD_FILE = sibpath(__file__, os.path.join("data", "no-xrd.xml"))

# None of the namespaces or service URIs below are official (or even
# sanctioned by the owners of that piece of URL-space)

LID_2_0 = "http://lid.netmesh.org/sso/2.0b5"
TYPEKEY_1_0 = "http://typekey.com/services/1.0"

def simpleOpenIDTransformer(endpoint):
    """Function to extract information from an OpenID service element"""
    if 'http://openid.net/signon/1.0' not in endpoint.type_uris:
        return None

    delegates = list(endpoint.service_element.findall(
        '{http://openid.net/xmlns/1.0}Delegate'))
    assert len(delegates) == 1
    delegate = delegates[0].text
    return (endpoint.uri, delegate)

class TestServiceParser(unittest.TestCase):
    def setUp(self):
        self.xmldoc = file(XRD_FILE).read()
        self.yadis_url = 'http://unittest.url/'

    def _getServices(self, flt=None):
        return list(services.applyFilter(self.yadis_url, self.xmldoc, flt))

    def testParse(self):
        """Make sure that parsing succeeds at all"""
        services = self._getServices()

    def testParseOpenID(self):
        """Parse for OpenID services with a transformer function"""
        services = self._getServices(simpleOpenIDTransformer)

        expectedServices = [
            ("http://www.myopenid.com/server", "http://josh.myopenid.com/"),
            ("http://www.schtuff.com/openid", "http://users.schtuff.com/josh"),
            ("http://www.livejournal.com/openid/server.bml",
             "http://www.livejournal.com/users/nedthealpaca/"),
            ]

        it = iter(services)
        for (server_url, delegate) in expectedServices:
            for (actual_url, actual_delegate) in it:
                self.failUnlessEqual(server_url, actual_url)
                self.failUnlessEqual(delegate, actual_delegate)
                break
            else:
                self.fail('Not enough services found')

    def _checkServices(self, expectedServices):
        """Check to make sure that the expected services are found in
        that order in the parsed document."""
        it = iter(self._getServices())
        for (type_uri, uri) in expectedServices:
            for service in it:
                if type_uri in service.type_uris:
                    self.failUnlessEqual(service.uri, uri)
                    break
            else:
                self.fail('Did not find %r service' % (type_uri,))

    def testGetSeveral(self):
        """Get some services in order"""
        expectedServices = [
            # type, URL
            (TYPEKEY_1_0, None),
            (LID_2_0, "http://mylid.net/josh"),
            ]

        self._checkServices(expectedServices)

    def testGetSeveralForOne(self):
        """Getting services for one Service with several Type elements."""
        types = [ 'http://lid.netmesh.org/sso/2.0b5'
                , 'http://lid.netmesh.org/2.0b5'
                ]

        uri = "http://mylid.net/josh"

        for service in self._getServices():
            if service.uri == uri:
                found_types = service.matchTypes(types)
                if found_types == types:
                    break
        else:
            self.fail('Did not find service with expected types and uris')

    def testNoXRDS(self):
        """Make sure that we get an exception when an XRDS element is
        not present"""
        self.xmldoc = file(NOXRDS_FILE).read()
        self.failUnlessRaises(
            etxrd.XRDSError,
            services.applyFilter, self.yadis_url, self.xmldoc, None)

    def testEmpty(self):
        """Make sure that we get an exception when an XRDS element is
        not present"""
        self.xmldoc = ''
        self.failUnlessRaises(
            etxrd.XRDSError,
            services.applyFilter, self.yadis_url, self.xmldoc, None)

    def testNoXRD(self):
        """Make sure that we get an exception when there is no XRD
        element present."""
        self.xmldoc = file(NOXRD_FILE).read()
        self.failUnlessRaises(
            etxrd.XRDSError,
            services.applyFilter, self.yadis_url, self.xmldoc, None)


class TestCanonicalID(unittest.TestCase):

    canonicalIDtests = [
        ("@ootao*test1", "delegated-20060809.xrds",
         "@!5BAD.2AA.3C72.AF46!0000.0000.3B9A.CA01"),
        ("@ootao*test1", "delegated-20060809-r1.xrds",
         "@!5BAD.2AA.3C72.AF46!0000.0000.3B9A.CA01"),
        ("@ootao*test1", "delegated-20060809-r2.xrds",
         "@!5BAD.2AA.3C72.AF46!0000.0000.3B9A.CA01"),
        ("@ootao*test1", "sometimesprefix.xrds",
         "@!5BAD.2AA.3C72.AF46!0000.0000.3B9A.CA01"),
        ("@ootao*test1", "prefixsometimes.xrds",
         "@!5BAD.2AA.3C72.AF46!0000.0000.3B9A.CA01"),
        ("=keturn*isDrummond", "spoof1.xrds", etxrd.XRDSFraud),
        ("=keturn*isDrummond", "spoof2.xrds", etxrd.XRDSFraud),
        ("@keturn*is*drummond", "spoof3.xrds", etxrd.XRDSFraud),
        ("=x", "status222.xrds", None),
        # Don't let IRI authorities be canonical for the GCS.
        ("phreak.example.com", "delegated-20060809-r2.xrds", etxrd.XRDSFraud),
        # TODO: Refs
        # ("@ootao*test.ref", "ref.xrds", "@!BAE.A650.823B.2475")
        ]

    # TODO: Add a IRI authority with an IRI canonicalID.
    # TODO: Add test cases with real examples of multiple CanonicalIDs
    #   somewhere in the resolution chain.

    def test_getCanonicalID(self):
        for iname, filename, expectedID in self.canonicalIDtests:
            filename = sibpath(__file__, os.path.join("data", filename))
            xrds = etxrd.parseXRDS(file(filename).read())
            self._getCanonicalID(iname, xrds, expectedID)


    def _getCanonicalID(self, iname, xrds, expectedID):
        if isinstance(expectedID, (str, unicode, type(None))):
            cid = etxrd.getCanonicalID(iname, xrds)
            self.failUnlessEqual(cid, expectedID and xri.XRI(expectedID))
        elif issubclass(expectedID, etxrd.XRDSError):
            self.failUnlessRaises(expectedID, etxrd.getCanonicalID,
                                  iname, xrds)
        else:
            self.fail("Don't know how to test for expected value %r"
                      % (expectedID,))


if __name__ == '__main__':
    unittest.main()
