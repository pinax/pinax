import unittest
from openid import message
from openid.test.support import OpenIDTestMixin
from openid.consumer import consumer
from openid.test.test_consumer import TestIdRes
from openid.consumer import discover

def const(result):
    """Return a function that ignores any arguments and just returns
    the specified result"""
    def constResult(*args, **kwargs):
        return result

    return constResult

class DiscoveryVerificationTest(OpenIDTestMixin, TestIdRes):
    def failUnlessProtocolError(self, prefix, callable, *args, **kwargs):
        try:
            result = callable(*args, **kwargs)
        except consumer.ProtocolError, e:
            self.failUnless(
                e[0].startswith(prefix),
                'Expected message prefix %r, got message %r' % (prefix, e[0]))
        else:
            self.fail('Expected ProtocolError with prefix %r, '
                      'got successful return %r' % (prefix, result))

    def test_openID1NoLocalID(self):
        endpoint = discover.OpenIDServiceEndpoint()
        endpoint.claimed_id = 'bogus'

        msg = message.Message.fromOpenIDArgs({})
        self.failUnlessProtocolError(
            'Missing required field openid.identity',
            self.consumer._verifyDiscoveryResults, msg, endpoint)
        self.failUnlessLogEmpty()

    def test_openID1NoEndpoint(self):
        msg = message.Message.fromOpenIDArgs({'identity':'snakes on a plane'})
        self.failUnlessRaises(RuntimeError,
                              self.consumer._verifyDiscoveryResults, msg)
        self.failUnlessLogEmpty()

    def test_openID2NoOPEndpointArg(self):
        msg = message.Message.fromOpenIDArgs({'ns':message.OPENID2_NS})
        self.failUnlessRaises(KeyError,
                              self.consumer._verifyDiscoveryResults, msg)
        self.failUnlessLogEmpty()

    def test_openID2LocalIDNoClaimed(self):
        msg = message.Message.fromOpenIDArgs({'ns':message.OPENID2_NS,
                                              'op_endpoint':'Phone Home',
                                              'identity':'Jose Lius Borges'})
        self.failUnlessProtocolError(
            'openid.identity is present without',
            self.consumer._verifyDiscoveryResults, msg)
        self.failUnlessLogEmpty()

    def test_openID2NoLocalIDClaimed(self):
        msg = message.Message.fromOpenIDArgs({'ns':message.OPENID2_NS,
                                              'op_endpoint':'Phone Home',
                                              'claimed_id':'Manuel Noriega'})
        self.failUnlessProtocolError(
            'openid.claimed_id is present without',
            self.consumer._verifyDiscoveryResults, msg)
        self.failUnlessLogEmpty()

    def test_openID2NoIdentifiers(self):
        op_endpoint = 'Phone Home'
        msg = message.Message.fromOpenIDArgs({'ns':message.OPENID2_NS,
                                              'op_endpoint':op_endpoint})
        result_endpoint = self.consumer._verifyDiscoveryResults(msg)
        self.failUnless(result_endpoint.isOPIdentifier())
        self.failUnlessEqual(op_endpoint, result_endpoint.server_url)
        self.failUnlessEqual(None, result_endpoint.claimed_id)
        self.failUnlessLogEmpty()

    def test_openID2NoEndpointDoesDisco(self):
        op_endpoint = 'Phone Home'
        sentinel = discover.OpenIDServiceEndpoint()
        sentinel.claimed_id = 'monkeysoft'
        self.consumer._discoverAndVerify = const(sentinel)
        msg = message.Message.fromOpenIDArgs(
            {'ns':message.OPENID2_NS,
             'identity':'sour grapes',
             'claimed_id':'monkeysoft',
             'op_endpoint':op_endpoint})
        result = self.consumer._verifyDiscoveryResults(msg)
        self.failUnlessEqual(sentinel, result)
        self.failUnlessLogMatches('No pre-discovered')

    def test_openID2MismatchedDoesDisco(self):
        mismatched = discover.OpenIDServiceEndpoint()
        mismatched.identity = 'nothing special, but different'
        mismatched.local_id = 'green cheese'

        op_endpoint = 'Phone Home'
        sentinel = discover.OpenIDServiceEndpoint()
        sentinel.claimed_id = 'monkeysoft'
        self.consumer._discoverAndVerify = const(sentinel)
        msg = message.Message.fromOpenIDArgs(
            {'ns':message.OPENID2_NS,
             'identity':'sour grapes',
             'claimed_id':'monkeysoft',
             'op_endpoint':op_endpoint})
        result = self.consumer._verifyDiscoveryResults(msg, mismatched)
        self.failUnlessEqual(sentinel, result)
        self.failUnlessLogMatches('Error attempting to use stored',
                                  'Attempting discovery')

    def test_openid2UsePreDiscovered(self):
        endpoint = discover.OpenIDServiceEndpoint()
        endpoint.local_id = 'my identity'
        endpoint.claimed_id = 'i am sam'
        endpoint.server_url = 'Phone Home'
        endpoint.type_uris = [discover.OPENID_2_0_TYPE]

        msg = message.Message.fromOpenIDArgs(
            {'ns':message.OPENID2_NS,
             'identity':endpoint.local_id,
             'claimed_id':endpoint.claimed_id,
             'op_endpoint':endpoint.server_url})
        result = self.consumer._verifyDiscoveryResults(msg, endpoint)
        self.failUnless(result is endpoint)
        self.failUnlessLogEmpty()

    def test_openid2UsePreDiscoveredWrongType(self):
        text = "verify failed"

        endpoint = discover.OpenIDServiceEndpoint()
        endpoint.local_id = 'my identity'
        endpoint.claimed_id = 'i am sam'
        endpoint.server_url = 'Phone Home'
        endpoint.type_uris = [discover.OPENID_1_1_TYPE]

        def discoverAndVerify(to_match):
            self.failUnlessEqual(endpoint.claimed_id, to_match.claimed_id)
            raise consumer.ProtocolError(text)

        self.consumer._discoverAndVerify = discoverAndVerify

        msg = message.Message.fromOpenIDArgs(
            {'ns':message.OPENID2_NS,
             'identity':endpoint.local_id,
             'claimed_id':endpoint.claimed_id,
             'op_endpoint':endpoint.server_url})

        try:
            r = self.consumer._verifyDiscoveryResults(msg, endpoint)
        except consumer.ProtocolError, e:
            # Should we make more ProtocolError subclasses?
            self.failUnless(str(e), text)
        else:
            self.fail("expected ProtocolError, %r returned." % (r,))

        self.failUnlessLogMatches('Error attempting to use stored',
                                  'Attempting discovery')

    def test_openid1UsePreDiscovered(self):
        endpoint = discover.OpenIDServiceEndpoint()
        endpoint.local_id = 'my identity'
        endpoint.claimed_id = 'i am sam'
        endpoint.server_url = 'Phone Home'
        endpoint.type_uris = [discover.OPENID_1_1_TYPE]

        msg = message.Message.fromOpenIDArgs(
            {'ns':message.OPENID1_NS,
             'identity':endpoint.local_id})
        result = self.consumer._verifyDiscoveryResults(msg, endpoint)
        self.failUnless(result is endpoint)
        self.failUnlessLogEmpty()

    def test_openid1UsePreDiscoveredWrongType(self):
        class VerifiedError(Exception): pass

        def discoverAndVerify(_to_match):
            raise VerifiedError

        self.consumer._discoverAndVerify = discoverAndVerify

        endpoint = discover.OpenIDServiceEndpoint()
        endpoint.local_id = 'my identity'
        endpoint.claimed_id = 'i am sam'
        endpoint.server_url = 'Phone Home'
        endpoint.type_uris = [discover.OPENID_2_0_TYPE]

        msg = message.Message.fromOpenIDArgs(
            {'ns':message.OPENID1_NS,
             'identity':endpoint.local_id})

        self.failUnlessRaises(
            VerifiedError,
            self.consumer._verifyDiscoveryResults, msg, endpoint)

        self.failUnlessLogMatches('Error attempting to use stored',
                                  'Attempting discovery')

    def test_openid2Fragment(self):
        claimed_id = "http://unittest.invalid/"
        claimed_id_frag = claimed_id + "#fragment"
        endpoint = discover.OpenIDServiceEndpoint()
        endpoint.local_id = 'my identity'
        endpoint.claimed_id = claimed_id
        endpoint.server_url = 'Phone Home'
        endpoint.type_uris = [discover.OPENID_2_0_TYPE]

        msg = message.Message.fromOpenIDArgs(
            {'ns':message.OPENID2_NS,
             'identity':endpoint.local_id,
             'claimed_id': claimed_id_frag,
             'op_endpoint': endpoint.server_url})
        result = self.consumer._verifyDiscoveryResults(msg, endpoint)
        
        self.failUnlessEqual(result.local_id, endpoint.local_id)
        self.failUnlessEqual(result.server_url, endpoint.server_url)
        self.failUnlessEqual(result.type_uris, endpoint.type_uris)

        self.failUnlessEqual(result.claimed_id, claimed_id_frag)
        
        self.failUnlessLogEmpty()


# XXX: test the implementation of _discoverAndVerify


class TestVerifyDiscoverySingle(TestIdRes):
    # XXX: more test the implementation of _verifyDiscoverySingle
    def test_endpointWithoutLocalID(self):
        # An endpoint like this with no local_id is generated as a result of
        # e.g. Yadis discovery with no LocalID tag.
        endpoint = discover.OpenIDServiceEndpoint()
        endpoint.server_url = "http://localhost:8000/openidserver"
        endpoint.claimed_id = "http://localhost:8000/id/id-jo"
        to_match = discover.OpenIDServiceEndpoint()
        to_match.server_url = "http://localhost:8000/openidserver"
        to_match.claimed_id = "http://localhost:8000/id/id-jo"
        to_match.local_id = "http://localhost:8000/id/id-jo"
        result = self.consumer._verifyDiscoverySingle(endpoint, to_match)
        # result should always be None, raises exception on failure.
        self.failUnlessEqual(result, None)
        self.failUnlessLogEmpty()

if __name__ == '__main__':
    unittest.main()
