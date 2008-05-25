import unittest
from openid.consumer.discover import \
     OpenIDServiceEndpoint, OPENID_1_1_TYPE, OPENID_1_0_TYPE

from openid.yadis.services import applyFilter


XRDS_BOILERPLATE = '''\
<?xml version="1.0" encoding="UTF-8"?>
<xrds:XRDS xmlns:xrds="xri://$xrds"
           xmlns="xri://$xrd*($v*2.0)"
           xmlns:openid="http://openid.net/xmlns/1.0">
    <XRD>
%s\
    </XRD>
</xrds:XRDS>
'''

def mkXRDS(services):
    return XRDS_BOILERPLATE % (services,)

def mkService(uris=None, type_uris=None, local_id=None, dent='        '):
    chunks = [dent, '<Service>\n']
    dent2 = dent + '    '
    if type_uris:
        for type_uri in type_uris:
            chunks.extend([dent2 + '<Type>', type_uri, '</Type>\n'])

    if uris:
        for uri in uris:
            if type(uri) is tuple:
                uri, prio = uri
            else:
                prio = None

            chunks.extend([dent2, '<URI'])
            if prio is not None:
                chunks.extend([' priority="', str(prio), '"'])
            chunks.extend(['>', uri, '</URI>\n'])

    if local_id:
        chunks.extend(
            [dent2, '<openid:Delegate>', local_id, '</openid:Delegate>\n'])

    chunks.extend([dent, '</Service>\n'])

    return ''.join(chunks)

# Different sets of server URLs for use in the URI tag
server_url_options = [
    [], # This case should not generate an endpoint object
    ['http://server.url/'],
    ['https://server.url/'],
    ['https://server.url/', 'http://server.url/'],
    ['https://server.url/',
     'http://server.url/',
     'http://example.server.url/'],
    ]

# Used for generating test data
def subsets(l):
    """Generate all non-empty sublists of a list"""
    subsets_list = [[]]
    for x in l:
        subsets_list += [[x] + t for t in subsets_list]
    return subsets_list

# A couple of example extension type URIs. These are not at all
# official, but are just here for testing.
ext_types = [
    'http://janrain.com/extension/blah',
    'http://openid.net/sreg/1.0',
    ]

# All valid combinations of Type tags that should produce an OpenID endpoint
type_uri_options = [
    exts + ts

    # All non-empty sublists of the valid OpenID type URIs
    for ts in subsets([OPENID_1_0_TYPE, OPENID_1_1_TYPE])
    if ts

    # All combinations of extension types (including empty extenstion list)
    for exts in subsets(ext_types)
    ]

# Range of valid Delegate tag values for generating test data
local_id_options = [
    None,
    'http://vanity.domain/',
    'https://somewhere/yadis/',
    ]

# All combinations of valid URIs, Type URIs and Delegate tags
data = [
    (uris, type_uris, local_id)
    for uris in server_url_options
    for type_uris in type_uri_options
    for local_id in local_id_options
    ]

class OpenIDYadisTest(unittest.TestCase):
    def __init__(self, uris, type_uris, local_id):
        unittest.TestCase.__init__(self)
        self.uris = uris
        self.type_uris = type_uris
        self.local_id = local_id

    def shortDescription(self):
        # XXX:
        return 'Successful OpenID Yadis parsing case'

    def setUp(self):
        self.yadis_url = 'http://unit.test/'

        # Create an XRDS document to parse
        services = mkService(uris=self.uris,
                             type_uris=self.type_uris,
                             local_id=self.local_id)
        self.xrds = mkXRDS(services)

    def runTest(self):
        # Parse into endpoint objects that we will check
        endpoints = applyFilter(
            self.yadis_url, self.xrds, OpenIDServiceEndpoint)

        # make sure there are the same number of endpoints as
        # URIs. This assumes that the type_uris contains at least one
        # OpenID type.
        self.failUnlessEqual(len(self.uris), len(endpoints))

        # So that we can check equality on the endpoint types
        type_uris = list(self.type_uris)
        type_uris.sort()

        seen_uris = []
        for endpoint in endpoints:
            seen_uris.append(endpoint.server_url)

            # All endpoints will have same yadis_url
            self.failUnlessEqual(self.yadis_url, endpoint.claimed_id)

            # and local_id
            self.failUnlessEqual(self.local_id, endpoint.local_id)

            # and types
            actual_types = list(endpoint.type_uris)
            actual_types.sort()
            self.failUnlessEqual(actual_types, type_uris)

        # So that they will compare equal, because we don't care what
        # order they are in
        seen_uris.sort()
        uris = list(self.uris)
        uris.sort()

        # Make sure we saw all URIs, and saw each one once
        self.failUnlessEqual(uris, seen_uris)

def pyUnitTests():
    cases = []
    for args in data:
        cases.append(OpenIDYadisTest(*args))
    return unittest.TestSuite(cases)
