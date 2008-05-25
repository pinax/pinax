
import unittest
from support import CatchLogs

from openid.message import Message, OPENID2_NS, OPENID1_NS, OPENID_NS
from openid import association
from openid.consumer.consumer import GenericConsumer, ServerError
from openid.consumer.discover import OpenIDServiceEndpoint, OPENID_2_0_TYPE

class ErrorRaisingConsumer(GenericConsumer):
    """
    A consumer whose _requestAssocation will return predefined results
    instead of trying to actually perform association requests.
    """

    # The list of objects to be returned by successive calls to
    # _requestAssocation.  Each call will pop the first element from
    # this list and return it to _negotiateAssociation.  If the
    # element is a Message object, it will be wrapped in a ServerError
    # exception.  Otherwise it will be returned as-is.
    return_messages = []

    def _requestAssociation(self, endpoint, assoc_type, session_type):
        m = self.return_messages.pop(0)
        if isinstance(m, Message):
            raise ServerError.fromMessage(m)
        else:
            return m

class TestOpenID2SessionNegotiation(unittest.TestCase, CatchLogs):
    """
    Test the session type negotiation behavior of an OpenID 2
    consumer.
    """
    def setUp(self):
        CatchLogs.setUp(self)
        self.consumer = ErrorRaisingConsumer(store=None)

        self.endpoint = OpenIDServiceEndpoint()
        self.endpoint.type_uris = [OPENID_2_0_TYPE]
        self.endpoint.server_url = 'bogus'

    def testBadResponse(self):
        """
        Test the case where the response to an associate request is a
        server error or is otherwise undecipherable.
        """
        self.consumer.return_messages = [Message(self.endpoint.preferredNamespace())]
        self.assertEqual(self.consumer._negotiateAssociation(self.endpoint), None)
        self.failUnlessLogMatches('Server error when requesting an association')

    def testEmptyAssocType(self):
        """
        Test the case where the association type (assoc_type) returned
        in an unsupported-type response is absent.
        """
        msg = Message(self.endpoint.preferredNamespace())
        msg.setArg(OPENID_NS, 'error', 'Unsupported type')
        msg.setArg(OPENID_NS, 'error_code', 'unsupported-type')
        # not set: msg.delArg(OPENID_NS, 'assoc_type')
        msg.setArg(OPENID_NS, 'session_type', 'new-session-type')

        self.consumer.return_messages = [msg]
        self.assertEqual(self.consumer._negotiateAssociation(self.endpoint), None)

        self.failUnlessLogMatches('Unsupported association type',
                                  'Server responded with unsupported association ' +
                                  'session but did not supply a fallback.')

    def testEmptySessionType(self):
        """
        Test the case where the session type (session_type) returned
        in an unsupported-type response is absent.
        """
        msg = Message(self.endpoint.preferredNamespace())
        msg.setArg(OPENID_NS, 'error', 'Unsupported type')
        msg.setArg(OPENID_NS, 'error_code', 'unsupported-type')
        msg.setArg(OPENID_NS, 'assoc_type', 'new-assoc-type')
        # not set: msg.setArg(OPENID_NS, 'session_type', None)

        self.consumer.return_messages = [msg]
        self.assertEqual(self.consumer._negotiateAssociation(self.endpoint), None)

        self.failUnlessLogMatches('Unsupported association type',
                                  'Server responded with unsupported association ' +
                                  'session but did not supply a fallback.')

    def testNotAllowed(self):
        """
        Test the case where an unsupported-type response specifies a
        preferred (assoc_type, session_type) combination that is not
        allowed by the consumer's SessionNegotiator.
        """
        allowed_types = []

        negotiator = association.SessionNegotiator(allowed_types)
        self.consumer.negotiator = negotiator

        msg = Message(self.endpoint.preferredNamespace())
        msg.setArg(OPENID_NS, 'error', 'Unsupported type')
        msg.setArg(OPENID_NS, 'error_code', 'unsupported-type')
        msg.setArg(OPENID_NS, 'assoc_type', 'not-allowed')
        msg.setArg(OPENID_NS, 'session_type', 'not-allowed')

        self.consumer.return_messages = [msg]
        self.assertEqual(self.consumer._negotiateAssociation(self.endpoint), None)

        self.failUnlessLogMatches('Unsupported association type',
                                  'Server sent unsupported session/association type:')

    def testUnsupportedWithRetry(self):
        """
        Test the case where an unsupported-type response triggers a
        retry to get an association with the new preferred type.
        """
        msg = Message(self.endpoint.preferredNamespace())
        msg.setArg(OPENID_NS, 'error', 'Unsupported type')
        msg.setArg(OPENID_NS, 'error_code', 'unsupported-type')
        msg.setArg(OPENID_NS, 'assoc_type', 'HMAC-SHA1')
        msg.setArg(OPENID_NS, 'session_type', 'DH-SHA1')

        assoc = association.Association(
            'handle', 'secret', 'issued', 10000, 'HMAC-SHA1')

        self.consumer.return_messages = [msg, assoc]
        self.failUnless(self.consumer._negotiateAssociation(self.endpoint) is assoc)

        self.failUnlessLogMatches('Unsupported association type')

    def testUnsupportedWithRetryAndFail(self):
        """
        Test the case where an unsupported-typ response triggers a
        retry, but the retry fails and None is returned instead.
        """
        msg = Message(self.endpoint.preferredNamespace())
        msg.setArg(OPENID_NS, 'error', 'Unsupported type')
        msg.setArg(OPENID_NS, 'error_code', 'unsupported-type')
        msg.setArg(OPENID_NS, 'assoc_type', 'HMAC-SHA1')
        msg.setArg(OPENID_NS, 'session_type', 'DH-SHA1')

        self.consumer.return_messages = [msg,
             Message(self.endpoint.preferredNamespace())]

        self.failUnlessEqual(self.consumer._negotiateAssociation(self.endpoint), None)

        self.failUnlessLogMatches('Unsupported association type',
                                  'Server %s refused' % (self.endpoint.server_url))

    def testValid(self):
        """
        Test the valid case, wherein an association is returned on the
        first attempt to get one.
        """
        assoc = association.Association(
            'handle', 'secret', 'issued', 10000, 'HMAC-SHA1')

        self.consumer.return_messages = [assoc]
        self.failUnless(self.consumer._negotiateAssociation(self.endpoint) is assoc)
        self.failUnlessLogEmpty()

class TestOpenID1SessionNegotiation(unittest.TestCase, CatchLogs):
    """
    Tests for the OpenID 1 consumer association session behavior.  See
    the docs for TestOpenID2SessionNegotiation.  Notice that this
    class is not a subclass of the OpenID 2 tests.  Instead, it uses
    many of the same inputs but inspects the log messages logged with
    oidutil.log.  See the calls to self.failUnlessLogMatches.  Some of
    these tests pass openid2-style messages to the openid 1
    association processing logic to be sure it ignores the extra data.
    """
    def setUp(self):
        CatchLogs.setUp(self)
        self.consumer = ErrorRaisingConsumer(store=None)

        self.endpoint = OpenIDServiceEndpoint()
        self.endpoint.type_uris = [OPENID1_NS]
        self.endpoint.server_url = 'bogus'

    def testBadResponse(self):
        self.consumer.return_messages = [Message(self.endpoint.preferredNamespace())]
        self.assertEqual(self.consumer._negotiateAssociation(self.endpoint), None)
        self.failUnlessLogMatches('Server error when requesting an association')

    def testEmptyAssocType(self):
        msg = Message(self.endpoint.preferredNamespace())
        msg.setArg(OPENID_NS, 'error', 'Unsupported type')
        msg.setArg(OPENID_NS, 'error_code', 'unsupported-type')
        # not set: msg.setArg(OPENID_NS, 'assoc_type', None)
        msg.setArg(OPENID_NS, 'session_type', 'new-session-type')

        self.consumer.return_messages = [msg]
        self.assertEqual(self.consumer._negotiateAssociation(self.endpoint), None)

        self.failUnlessLogMatches('Server error when requesting an association')

    def testEmptySessionType(self):
        msg = Message(self.endpoint.preferredNamespace())
        msg.setArg(OPENID_NS, 'error', 'Unsupported type')
        msg.setArg(OPENID_NS, 'error_code', 'unsupported-type')
        msg.setArg(OPENID_NS, 'assoc_type', 'new-assoc-type')
        # not set: msg.setArg(OPENID_NS, 'session_type', None)

        self.consumer.return_messages = [msg]
        self.assertEqual(self.consumer._negotiateAssociation(self.endpoint), None)

        self.failUnlessLogMatches('Server error when requesting an association')

    def testNotAllowed(self):
        allowed_types = []

        negotiator = association.SessionNegotiator(allowed_types)
        self.consumer.negotiator = negotiator

        msg = Message(self.endpoint.preferredNamespace())
        msg.setArg(OPENID_NS, 'error', 'Unsupported type')
        msg.setArg(OPENID_NS, 'error_code', 'unsupported-type')
        msg.setArg(OPENID_NS, 'assoc_type', 'not-allowed')
        msg.setArg(OPENID_NS, 'session_type', 'not-allowed')

        self.consumer.return_messages = [msg]
        self.assertEqual(self.consumer._negotiateAssociation(self.endpoint), None)

        self.failUnlessLogMatches('Server error when requesting an association')

    def testUnsupportedWithRetry(self):
        msg = Message(self.endpoint.preferredNamespace())
        msg.setArg(OPENID_NS, 'error', 'Unsupported type')
        msg.setArg(OPENID_NS, 'error_code', 'unsupported-type')
        msg.setArg(OPENID_NS, 'assoc_type', 'HMAC-SHA1')
        msg.setArg(OPENID_NS, 'session_type', 'DH-SHA1')

        assoc = association.Association(
            'handle', 'secret', 'issued', 10000, 'HMAC-SHA1')

        self.consumer.return_messages = [msg, assoc]
        self.failUnless(self.consumer._negotiateAssociation(self.endpoint) is None)

        self.failUnlessLogMatches('Server error when requesting an association')

    def testValid(self):
        assoc = association.Association(
            'handle', 'secret', 'issued', 10000, 'HMAC-SHA1')

        self.consumer.return_messages = [assoc]
        self.failUnless(self.consumer._negotiateAssociation(self.endpoint) is assoc)
        self.failUnlessLogEmpty()

class TestNegotiatorBehaviors(unittest.TestCase, CatchLogs):
    def setUp(self):
        self.allowed_types = [
            ('HMAC-SHA1', 'no-encryption'),
            ('HMAC-SHA256', 'no-encryption'),
            ]

        self.n = association.SessionNegotiator(self.allowed_types)

    def testAddAllowedTypeNoSessionTypes(self):
        self.assertRaises(ValueError, self.n.addAllowedType, 'invalid')

    def testAddAllowedTypeBadSessionType(self):
        self.assertRaises(ValueError, self.n.addAllowedType, 'assoc1', 'invalid')

    def testAddAllowedTypeContents(self):
        assoc_type = 'HMAC-SHA1'
        self.failUnless(self.n.addAllowedType(assoc_type) is None)

        for typ in association.getSessionTypes(assoc_type):
            self.failUnless((assoc_type, typ) in self.n.allowed_types)

if __name__ == '__main__':
    unittest.main()
