"""Tests for consumer handling of association responses

This duplicates some things that are covered by test_consumer, but
this works for now.
"""
from openid import oidutil
from openid.test.test_consumer import CatchLogs
from openid.message import Message, OPENID2_NS, OPENID_NS, no_default
from openid.server.server import DiffieHellmanSHA1ServerSession
from openid.consumer.consumer import GenericConsumer, \
     DiffieHellmanSHA1ConsumerSession, ProtocolError
from openid.consumer.discover import OpenIDServiceEndpoint, OPENID_1_1_TYPE, OPENID_2_0_TYPE
from openid.store import memstore
import unittest

# Some values we can use for convenience (see mkAssocResponse)
association_response_values = {
    'expires_in': '1000',
    'assoc_handle':'a handle',
    'assoc_type':'a type',
    'session_type':'a session type',
    'ns':OPENID2_NS,
    }

def mkAssocResponse(*keys):
    """Build an association response message that contains the
    specified subset of keys. The values come from
    `association_response_values`.

    This is useful for testing for missing keys and other times that
    we don't care what the values are."""
    args = dict([(key, association_response_values[key]) for key in keys])
    return Message.fromOpenIDArgs(args)

class BaseAssocTest(CatchLogs, unittest.TestCase):
    def setUp(self):
        CatchLogs.setUp(self)
        self.store = memstore.MemoryStore()
        self.consumer = GenericConsumer(self.store)
        self.endpoint = OpenIDServiceEndpoint()

    def failUnlessProtocolError(self, str_prefix, func, *args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except ProtocolError, e:
            message = 'Expected prefix %r, got %r' % (str_prefix, e[0])
            self.failUnless(e[0].startswith(str_prefix), message)
        else:
            self.fail('Expected ProtocolError, got %r' % (result,))

def mkExtractAssocMissingTest(keys):
    """Factory function for creating test methods for generating
    missing field tests.

    Make a test that ensures that an association response that
    is missing required fields will short-circuit return None.

    According to 'Association Session Response' subsection 'Common
    Response Parameters', the following fields are required for OpenID
    2.0:

     * ns
     * session_type
     * assoc_handle
     * assoc_type
     * expires_in

    If 'ns' is missing, it will fall back to OpenID 1 checking. In
    OpenID 1, everything except 'session_type' and 'ns' are required.
    """

    def test(self):
        msg = mkAssocResponse(*keys)

        self.failUnlessRaises(KeyError,
                              self.consumer._extractAssociation, msg, None)

    return test

class TestExtractAssociationMissingFieldsOpenID2(BaseAssocTest):
    """Test for returning an error upon missing fields in association
    responses for OpenID 2"""

    test_noFields_openid2 = mkExtractAssocMissingTest(['ns'])

    test_missingExpires_openid2 = mkExtractAssocMissingTest(
        ['assoc_handle', 'assoc_type', 'session_type', 'ns'])

    test_missingHandle_openid2 = mkExtractAssocMissingTest(
        ['expires_in', 'assoc_type', 'session_type', 'ns'])

    test_missingAssocType_openid2 = mkExtractAssocMissingTest(
        ['expires_in', 'assoc_handle', 'session_type', 'ns'])

    test_missingSessionType_openid2 = mkExtractAssocMissingTest(
        ['expires_in', 'assoc_handle', 'assoc_type', 'ns'])

class TestExtractAssociationMissingFieldsOpenID1(BaseAssocTest):
    """Test for returning an error upon missing fields in association
    responses for OpenID 2"""

    test_noFields_openid1 = mkExtractAssocMissingTest([])

    test_missingExpires_openid1 = mkExtractAssocMissingTest(
        ['assoc_handle', 'assoc_type'])

    test_missingHandle_openid1 = mkExtractAssocMissingTest(
        ['expires_in', 'assoc_type'])

    test_missingAssocType_openid1 = mkExtractAssocMissingTest(
        ['expires_in', 'assoc_handle'])

class DummyAssocationSession(object):
    def __init__(self, session_type, allowed_assoc_types=()):
        self.session_type = session_type
        self.allowed_assoc_types = allowed_assoc_types

class ExtractAssociationSessionTypeMismatch(BaseAssocTest):
    def mkTest(requested_session_type, response_session_type, openid1=False):
        def test(self):
            assoc_session = DummyAssocationSession(requested_session_type)
            keys = association_response_values.keys()
            if openid1:
                keys.remove('ns')
            msg = mkAssocResponse(*keys)
            msg.setArg(OPENID_NS, 'session_type', response_session_type)
            self.failUnlessProtocolError('Session type mismatch',
                self.consumer._extractAssociation, msg, assoc_session)

        return test

    test_typeMismatchNoEncBlank_openid2 = mkTest(
        requested_session_type='no-encryption',
        response_session_type='',
        )

    test_typeMismatchDHSHA1NoEnc_openid2 = mkTest(
        requested_session_type='DH-SHA1',
        response_session_type='no-encryption',
        )

    test_typeMismatchDHSHA256NoEnc_openid2 = mkTest(
        requested_session_type='DH-SHA256',
        response_session_type='no-encryption',
        )

    test_typeMismatchNoEncDHSHA1_openid2 = mkTest(
        requested_session_type='no-encryption',
        response_session_type='DH-SHA1',
        )

    test_typeMismatchDHSHA1NoEnc_openid1 = mkTest(
        requested_session_type='DH-SHA1',
        response_session_type='DH-SHA256',
        openid1=True,
        )

    test_typeMismatchDHSHA256NoEnc_openid1 = mkTest(
        requested_session_type='DH-SHA256',
        response_session_type='DH-SHA1',
        openid1=True,
        )

    test_typeMismatchNoEncDHSHA1_openid1 = mkTest(
        requested_session_type='no-encryption',
        response_session_type='DH-SHA1',
        openid1=True,
        )


class TestOpenID1AssociationResponseSessionType(BaseAssocTest):
    def mkTest(expected_session_type, session_type_value):
        """Return a test method that will check what session type will
        be used if the OpenID 1 response to an associate call sets the
        'session_type' field to `session_type_value`
        """
        def test(self):
            self._doTest(expected_session_type, session_type_value)
            self.failUnlessEqual(0, len(self.messages))

        return test

    def _doTest(self, expected_session_type, session_type_value):
        # Create a Message with just 'session_type' in it, since
        # that's all this function will use. 'session_type' may be
        # absent if it's set to None.
        args = {}
        if session_type_value is not None:
            args['session_type'] = session_type_value
        message = Message.fromOpenIDArgs(args)
        self.failUnless(message.isOpenID1())

        actual_session_type = self.consumer._getOpenID1SessionType(message)
        error_message = ('Returned sesion type parameter %r was expected '
                         'to yield session type %r, but yielded %r' %
                         (session_type_value, expected_session_type,
                          actual_session_type))
        self.failUnlessEqual(
            expected_session_type, actual_session_type, error_message)

    test_none = mkTest(
        session_type_value=None,
        expected_session_type='no-encryption',
        )

    test_empty = mkTest(
        session_type_value='',
        expected_session_type='no-encryption',
        )

    # This one's different because it expects log messages
    def test_explicitNoEncryption(self):
        self._doTest(
            session_type_value='no-encryption',
            expected_session_type='no-encryption',
            )
        self.failUnlessEqual(1, len(self.messages))
        self.failUnless(self.messages[0].startswith(
            'WARNING: OpenID server sent "no-encryption"'))

    test_dhSHA1 = mkTest(
        session_type_value='DH-SHA1',
        expected_session_type='DH-SHA1',
        )

    # DH-SHA256 is not a valid session type for OpenID1, but this
    # function does not test that. This is mostly just to make sure
    # that it will pass-through stuff that is not explicitly handled,
    # so it will get handled the same way as it is handled for OpenID
    # 2
    test_dhSHA256 = mkTest(
        session_type_value='DH-SHA256',
        expected_session_type='DH-SHA256',
        )

class DummyAssociationSession(object):
    secret = "shh! don't tell!"
    extract_secret_called = False

    session_type = None

    allowed_assoc_types = None

    def extractSecret(self, message):
        self.extract_secret_called = True
        return self.secret

class TestInvalidFields(BaseAssocTest):
    def setUp(self):
        BaseAssocTest.setUp(self)
        self.session_type = 'testing-session'

        # This must something that works for Association.fromExpiresIn
        self.assoc_type = 'HMAC-SHA1'

        self.assoc_handle = 'testing-assoc-handle'

        # These arguments should all be valid
        self.assoc_response = Message.fromOpenIDArgs({
            'expires_in': '1000',
            'assoc_handle':self.assoc_handle,
            'assoc_type':self.assoc_type,
            'session_type':self.session_type,
            'ns':OPENID2_NS,
            })

        self.assoc_session = DummyAssociationSession()

        # Make the session for the response's session type
        self.assoc_session.session_type = self.session_type
        self.assoc_session.allowed_assoc_types = [self.assoc_type]

    def test_worksWithGoodFields(self):
        """Handle a full successful association response"""
        assoc = self.consumer._extractAssociation(
            self.assoc_response, self.assoc_session)
        self.failUnless(self.assoc_session.extract_secret_called)
        self.failUnlessEqual(self.assoc_session.secret, assoc.secret)
        self.failUnlessEqual(1000, assoc.lifetime)
        self.failUnlessEqual(self.assoc_handle, assoc.handle)
        self.failUnlessEqual(self.assoc_type, assoc.assoc_type)

    def test_badAssocType(self):
        # Make sure that the assoc type in the response is not valid
        # for the given session.
        self.assoc_session.allowed_assoc_types = []
        self.failUnlessProtocolError('Unsupported assoc_type for session',
            self.consumer._extractAssociation,
            self.assoc_response, self.assoc_session)

    def test_badExpiresIn(self):
        # Invalid value for expires_in should cause failure
        self.assoc_response.setArg(OPENID_NS, 'expires_in', 'forever')
        self.failUnlessProtocolError('Invalid expires_in',
            self.consumer._extractAssociation,
            self.assoc_response, self.assoc_session)


# XXX: This is what causes most of the imports in this file. It is
# sort of a unit test and sort of a functional test. I'm not terribly
# fond of it.
class TestExtractAssociationDiffieHellman(BaseAssocTest):
    secret = 'x' * 20

    def _setUpDH(self):
        sess, message = self.consumer._createAssociateRequest(
            self.endpoint, 'HMAC-SHA1', 'DH-SHA1')

        # XXX: this is testing _createAssociateRequest
        self.failUnlessEqual(self.endpoint.compatibilityMode(),
                             message.isOpenID1())

        server_sess = DiffieHellmanSHA1ServerSession.fromMessage(message)
        server_resp = server_sess.answer(self.secret)
        server_resp['assoc_type'] = 'HMAC-SHA1'
        server_resp['assoc_handle'] = 'handle'
        server_resp['expires_in'] = '1000'
        server_resp['session_type'] = 'DH-SHA1'
        return sess, Message.fromOpenIDArgs(server_resp)

    def test_success(self):
        sess, server_resp = self._setUpDH()
        ret = self.consumer._extractAssociation(server_resp, sess)
        self.failIf(ret is None)
        self.failUnlessEqual(ret.assoc_type, 'HMAC-SHA1')
        self.failUnlessEqual(ret.secret, self.secret)
        self.failUnlessEqual(ret.handle, 'handle')
        self.failUnlessEqual(ret.lifetime, 1000)

    def test_openid2success(self):
        # Use openid 2 type in endpoint so _setUpDH checks
        # compatibility mode state properly
        self.endpoint.type_uris = [OPENID_2_0_TYPE, OPENID_1_1_TYPE]
        self.test_success()

    def test_badDHValues(self):
        sess, server_resp = self._setUpDH()
        server_resp.setArg(OPENID_NS, 'enc_mac_key', '\x00\x00\x00')
        self.failUnlessProtocolError('Malformed response for',
            self.consumer._extractAssociation, server_resp, sess)
