import urlparse
import cgi
import time
import warnings

from openid.message import Message, OPENID_NS, OPENID2_NS, IDENTIFIER_SELECT, \
     OPENID1_NS, BARE_NS
from openid import cryptutil, dh, oidutil, kvform
from openid.store.nonce import mkNonce, split as splitNonce
from openid.consumer.discover import OpenIDServiceEndpoint, OPENID_2_0_TYPE, \
     OPENID_1_1_TYPE
from openid.consumer.consumer import \
     AuthRequest, GenericConsumer, SUCCESS, FAILURE, CANCEL, SETUP_NEEDED, \
     SuccessResponse, FailureResponse, SetupNeededResponse, CancelResponse, \
     DiffieHellmanSHA1ConsumerSession, Consumer, PlainTextConsumerSession, \
     SetupNeededError, DiffieHellmanSHA256ConsumerSession, ServerError, \
     ProtocolError, _httpResponseToMessage
from openid import association
from openid.server.server import \
     PlainTextServerSession, DiffieHellmanSHA1ServerSession
from openid.yadis.manager import Discovery
from openid.yadis.discover import DiscoveryFailure
from openid.dh import DiffieHellman

from openid.fetchers import HTTPResponse, HTTPFetchingError
from openid import fetchers
from openid.store import memstore

from support import CatchLogs

assocs = [
    ('another 20-byte key.', 'Snarky'),
    ('\x00' * 20, 'Zeros'),
    ]

def mkSuccess(endpoint, q):
    """Convenience function to create a SuccessResponse with the given
    arguments, all signed."""
    signed_list = ['openid.' + k for k in q.keys()]
    return SuccessResponse(endpoint, Message.fromOpenIDArgs(q), signed_list)

def parseQuery(qs):
    q = {}
    for (k, v) in cgi.parse_qsl(qs):
        assert not q.has_key(k)
        q[k] = v
    return q

def associate(qs, assoc_secret, assoc_handle):
    """Do the server's half of the associate call, using the given
    secret and handle."""
    q = parseQuery(qs)
    assert q['openid.mode'] == 'associate'
    assert q['openid.assoc_type'] == 'HMAC-SHA1'
    reply_dict = {
        'assoc_type':'HMAC-SHA1',
        'assoc_handle':assoc_handle,
        'expires_in':'600',
        }

    if q.get('openid.session_type') == 'DH-SHA1':
        assert len(q) == 6 or len(q) == 4
        message = Message.fromPostArgs(q)
        session = DiffieHellmanSHA1ServerSession.fromMessage(message)
        reply_dict['session_type'] = 'DH-SHA1'
    else:
        assert len(q) == 2
        session = PlainTextServerSession.fromQuery(q)

    reply_dict.update(session.answer(assoc_secret))
    return kvform.dictToKV(reply_dict)


GOODSIG = "[A Good Signature]"


class GoodAssociation:
    expiresIn = 3600
    handle = "-blah-"

    def getExpiresIn(self):
        return self.expiresIn

    def checkMessageSignature(self, message):
        return message.getArg(OPENID_NS, 'sig') == GOODSIG


class GoodAssocStore(memstore.MemoryStore):
    def getAssociation(self, server_url, handle=None):
        return GoodAssociation()


class TestFetcher(object):
    def __init__(self, user_url, user_page, (assoc_secret, assoc_handle)):
        self.get_responses = {user_url:self.response(user_url, 200, user_page)}
        self.assoc_secret = assoc_secret
        self.assoc_handle = assoc_handle
        self.num_assocs = 0

    def response(self, url, status, body):
        return HTTPResponse(
            final_url=url, status=status, headers={}, body=body)

    def fetch(self, url, body=None, headers=None):
        if body is None:
            if url in self.get_responses:
                return self.get_responses[url]
        else:
            try:
                body.index('openid.mode=associate')
            except ValueError:
                pass # fall through
            else:
                assert body.find('DH-SHA1') != -1
                response = associate(
                    body, self.assoc_secret, self.assoc_handle)
                self.num_assocs += 1
                return self.response(url, 200, response)

        return self.response(url, 404, 'Not found')

def makeFastConsumerSession():
    """
    Create custom DH object so tests run quickly.
    """
    dh = DiffieHellman(100389557, 2)
    return DiffieHellmanSHA1ConsumerSession(dh)

def setConsumerSession(con):
    con.session_types = {'DH-SHA1': makeFastConsumerSession}

def _test_success(server_url, user_url, delegate_url, links, immediate=False):
    store = memstore.MemoryStore()
    if immediate:
        mode = 'checkid_immediate'
    else:
        mode = 'checkid_setup'

    endpoint = OpenIDServiceEndpoint()
    endpoint.claimed_id = user_url
    endpoint.server_url = server_url
    endpoint.local_id = delegate_url
    endpoint.type_uris = [OPENID_1_1_TYPE]

    fetcher = TestFetcher(None, None, assocs[0])
    fetchers.setDefaultFetcher(fetcher, wrap_exceptions=False)

    def run():
        trust_root = consumer_url

        consumer = GenericConsumer(store)
        setConsumerSession(consumer)

        request = consumer.begin(endpoint)
        return_to = consumer_url

        m = request.getMessage(trust_root, return_to, immediate)

        redirect_url = request.redirectURL(trust_root, return_to, immediate)

        parsed = urlparse.urlparse(redirect_url)
        qs = parsed[4]
        q = parseQuery(qs)
        new_return_to = q['openid.return_to']
        del q['openid.return_to']
        assert q == {
            'openid.mode':mode,
            'openid.identity':delegate_url,
            'openid.trust_root':trust_root,
            'openid.assoc_handle':fetcher.assoc_handle,
            }, (q, user_url, delegate_url, mode)

        assert new_return_to.startswith(return_to)
        assert redirect_url.startswith(server_url)

        parsed = urlparse.urlparse(new_return_to)
        query = parseQuery(parsed[4])
        query.update({
            'openid.mode':'id_res',
            'openid.return_to':new_return_to,
            'openid.identity':delegate_url,
            'openid.assoc_handle':fetcher.assoc_handle,
            })

        assoc = store.getAssociation(server_url, fetcher.assoc_handle)

        message = Message.fromPostArgs(query)
        message = assoc.signMessage(message)
        info = consumer.complete(message, request.endpoint, new_return_to)
        assert info.status == SUCCESS, info.message
        assert info.identity_url == user_url

    assert fetcher.num_assocs == 0
    run()
    assert fetcher.num_assocs == 1

    # Test that doing it again uses the existing association
    run()
    assert fetcher.num_assocs == 1

    # Another association is created if we remove the existing one
    store.removeAssociation(server_url, fetcher.assoc_handle)
    run()
    assert fetcher.num_assocs == 2

    # Test that doing it again uses the existing association
    run()
    assert fetcher.num_assocs == 2

import unittest

http_server_url = 'http://server.example.com/'
consumer_url = 'http://consumer.example.com/'
https_server_url = 'https://server.example.com/'

class TestSuccess(unittest.TestCase, CatchLogs):
    server_url = http_server_url
    user_url = 'http://www.example.com/user.html'
    delegate_url = 'http://consumer.example.com/user'

    def setUp(self):
        CatchLogs.setUp(self)
        self.links = '<link rel="openid.server" href="%s" />' % (
            self.server_url,)

        self.delegate_links = ('<link rel="openid.server" href="%s" />'
                               '<link rel="openid.delegate" href="%s" />') % (
            self.server_url, self.delegate_url)

    def tearDown(self):
        CatchLogs.tearDown(self)

    def test_nodelegate(self):
        _test_success(self.server_url, self.user_url,
                      self.user_url, self.links)

    def test_nodelegateImmediate(self):
        _test_success(self.server_url, self.user_url,
                      self.user_url, self.links, True)

    def test_delegate(self):
        _test_success(self.server_url, self.user_url,
                      self.delegate_url, self.delegate_links)

    def test_delegateImmediate(self):
        _test_success(self.server_url, self.user_url,
                      self.delegate_url, self.delegate_links, True)


class TestSuccessHTTPS(TestSuccess):
    server_url = https_server_url


class TestConstruct(unittest.TestCase):
    def setUp(self):
        self.store_sentinel = object()

    def test_construct(self):
        oidc = GenericConsumer(self.store_sentinel)
        self.failUnless(oidc.store is self.store_sentinel)

    def test_nostore(self):
        self.failUnlessRaises(TypeError, GenericConsumer)


class TestIdRes(unittest.TestCase, CatchLogs):
    consumer_class = GenericConsumer

    def setUp(self):
        CatchLogs.setUp(self)

        self.store = memstore.MemoryStore()
        self.consumer = self.consumer_class(self.store)
        self.return_to = "nonny"
        self.endpoint = OpenIDServiceEndpoint()
        self.endpoint.claimed_id = self.consumer_id = "consu"
        self.endpoint.server_url = self.server_url = "serlie"
        self.endpoint.local_id = self.server_id = "sirod"
        self.endpoint.type_uris = [OPENID_1_1_TYPE]

    def disableDiscoveryVerification(self):
        """Set the discovery verification to a no-op for test cases in
        which we don't care."""
        def dummyVerifyDiscover(_, endpoint):
            return endpoint
        self.consumer._verifyDiscoveryResults = dummyVerifyDiscover

    def disableReturnToChecking(self):
        def checkReturnTo(unused1, unused2):
            return True
        self.consumer._checkReturnTo = checkReturnTo
        complete = self.consumer.complete
        def callCompleteWithoutReturnTo(message, endpoint):
            return complete(message, endpoint, None)
        self.consumer.complete = callCompleteWithoutReturnTo

class TestIdResCheckSignature(TestIdRes):
    def setUp(self):
        TestIdRes.setUp(self)
        self.assoc = GoodAssociation()
        self.assoc.handle = "{not_dumb}"
        self.store.storeAssociation(self.endpoint.server_url, self.assoc)

        self.message = Message.fromPostArgs({
            'openid.mode': 'id_res',
            'openid.identity': '=example',
            'openid.sig': GOODSIG,
            'openid.assoc_handle': self.assoc.handle,
            'openid.signed': 'mode,identity,assoc_handle,signed',
            'frobboz': 'banzit',
            })


    def test_sign(self):
        # assoc_handle to assoc with good sig
        self.consumer._idResCheckSignature(self.message,
                                           self.endpoint.server_url)


    def test_signFailsWithBadSig(self):
        self.message.setArg(OPENID_NS, 'sig', 'BAD SIGNATURE')
        self.failUnlessRaises(
            ProtocolError, self.consumer._idResCheckSignature,
            self.message, self.endpoint.server_url)


    def test_stateless(self):
        # assoc_handle missing assoc, consumer._checkAuth returns goodthings
        self.message.setArg(OPENID_NS, "assoc_handle", "dumbHandle")
        self.consumer._processCheckAuthResponse = (
            lambda response, server_url: True)
        self.consumer._makeKVPost = lambda args, server_url: {}
        self.consumer._idResCheckSignature(self.message,
                                           self.endpoint.server_url)

    def test_statelessRaisesError(self):
        # assoc_handle missing assoc, consumer._checkAuth returns goodthings
        self.message.setArg(OPENID_NS, "assoc_handle", "dumbHandle")
        self.consumer._checkAuth = lambda unused1, unused2: False
        self.failUnlessRaises(
            ProtocolError, self.consumer._idResCheckSignature,
            self.message, self.endpoint.server_url)

    def test_stateless_noStore(self):
        # assoc_handle missing assoc, consumer._checkAuth returns goodthings
        self.message.setArg(OPENID_NS, "assoc_handle", "dumbHandle")
        self.consumer.store = None
        self.consumer._processCheckAuthResponse = (
            lambda response, server_url: True)
        self.consumer._makeKVPost = lambda args, server_url: {}
        self.consumer._idResCheckSignature(self.message,
                                           self.endpoint.server_url)

    def test_statelessRaisesError_noStore(self):
        # assoc_handle missing assoc, consumer._checkAuth returns goodthings
        self.message.setArg(OPENID_NS, "assoc_handle", "dumbHandle")
        self.consumer._checkAuth = lambda unused1, unused2: False
        self.consumer.store = None
        self.failUnlessRaises(
            ProtocolError, self.consumer._idResCheckSignature,
            self.message, self.endpoint.server_url)


class TestQueryFormat(TestIdRes):
    def test_notAList(self):
        # XXX: should be a Message object test, not a consumer test

        # Value should be a single string.  If it's a list, it should generate
        # an exception.
        query = {'openid.mode': ['cancel']}
        try:
            r = Message.fromPostArgs(query)
        except TypeError, err:
            self.failUnless(str(err).find('values') != -1, err)
        else:
            self.fail("expected TypeError, got this instead: %s" % (r,))

class TestComplete(TestIdRes):
    """Testing GenericConsumer.complete.

    Other TestIdRes subclasses test more specific aspects.
    """

    def test_setupNeededIdRes(self):
        message = Message.fromOpenIDArgs({'mode': 'id_res'})
        setup_url_sentinel = object()

        def raiseSetupNeeded(msg):
            self.failUnless(msg is message)
            raise SetupNeededError(setup_url_sentinel)

        self.consumer._checkSetupNeeded = raiseSetupNeeded

        response = self.consumer.complete(message, None, None)
        self.failUnlessEqual(SETUP_NEEDED, response.status)
        self.failUnless(setup_url_sentinel is response.setup_url)

    def test_cancel(self):
        message = Message.fromPostArgs({'openid.mode': 'cancel'})
        self.disableReturnToChecking()
        r = self.consumer.complete(message, self.endpoint)
        self.failUnlessEqual(r.status, CANCEL)
        self.failUnless(r.identity_url == self.endpoint.claimed_id)

    def test_cancel_with_return_to(self):
        message = Message.fromPostArgs({'openid.mode': 'cancel'})
        r = self.consumer.complete(message, self.endpoint, self.return_to)
        self.failUnlessEqual(r.status, CANCEL)
        self.failUnless(r.identity_url == self.endpoint.claimed_id)

    def test_error(self):
        msg = 'an error message'
        message = Message.fromPostArgs({'openid.mode': 'error',
                 'openid.error': msg,
                 })
        self.disableReturnToChecking()
        r = self.consumer.complete(message, self.endpoint)
        self.failUnlessEqual(r.status, FAILURE)
        self.failUnless(r.identity_url == self.endpoint.claimed_id)
        self.failUnlessEqual(r.message, msg)

    def test_errorWithNoOptionalKeys(self):
        msg = 'an error message'
        contact = 'some contact info here'
        message = Message.fromPostArgs({'openid.mode': 'error',
                 'openid.error': msg,
                 'openid.contact': contact,
                 })
        self.disableReturnToChecking()
        r = self.consumer.complete(message, self.endpoint)
        self.failUnlessEqual(r.status, FAILURE)
        self.failUnless(r.identity_url == self.endpoint.claimed_id)
        self.failUnless(r.contact == contact)
        self.failUnless(r.reference is None)
        self.failUnlessEqual(r.message, msg)

    def test_errorWithOptionalKeys(self):
        msg = 'an error message'
        contact = 'me'
        reference = 'support ticket'
        message = Message.fromPostArgs({'openid.mode': 'error',
                 'openid.error': msg, 'openid.reference': reference,
                 'openid.contact': contact, 'openid.ns': OPENID2_NS,
                 })
        r = self.consumer.complete(message, self.endpoint, None)
        self.failUnlessEqual(r.status, FAILURE)
        self.failUnless(r.identity_url == self.endpoint.claimed_id)
        self.failUnless(r.contact == contact)
        self.failUnless(r.reference == reference)
        self.failUnlessEqual(r.message, msg)

    def test_noMode(self):
        message = Message.fromPostArgs({})
        r = self.consumer.complete(message, self.endpoint, None)
        self.failUnlessEqual(r.status, FAILURE)
        self.failUnless(r.identity_url == self.endpoint.claimed_id)

    def test_idResMissingField(self):
        # XXX - this test is passing, but not necessarily by what it
        # is supposed to test for.  status in FAILURE, but it's because
        # *check_auth* failed, not because it's missing an arg, exactly.
        message = Message.fromPostArgs({'openid.mode': 'id_res'})
        self.failUnlessRaises(ProtocolError, self.consumer._doIdRes,
                              message, self.endpoint, None)

    def test_idResURLMismatch(self):
        class VerifiedError(Exception): pass

        def discoverAndVerify(_to_match):
            raise VerifiedError

        self.consumer._discoverAndVerify = discoverAndVerify
        self.disableReturnToChecking()

        message = Message.fromPostArgs(
            {'openid.mode': 'id_res',
             'openid.return_to': 'return_to (just anything)',
             'openid.identity': 'something wrong (not self.consumer_id)',
             'openid.assoc_handle': 'does not matter',
             'openid.sig': GOODSIG,
             'openid.signed': 'identity,return_to',
             })
        self.consumer.store = GoodAssocStore()

        self.failUnlessRaises(VerifiedError,
                              self.consumer.complete,
                              message, self.endpoint)

        self.failUnlessLogMatches('Error attempting to use stored',
                                  'Attempting discovery')

class TestCompleteMissingSig(unittest.TestCase, CatchLogs):

    def setUp(self):
        self.store = GoodAssocStore()
        self.consumer = GenericConsumer(self.store)
        self.server_url = "http://idp.unittest/"
        CatchLogs.setUp(self)

        claimed_id = 'bogus.claimed'

        self.message = Message.fromOpenIDArgs(
            {'mode': 'id_res',
             'return_to': 'return_to (just anything)',
             'identity': claimed_id,
             'assoc_handle': 'does not matter',
             'sig': GOODSIG,
             'response_nonce': mkNonce(),
             'signed': 'identity,return_to,response_nonce,assoc_handle,claimed_id',
             'claimed_id': claimed_id,
             'op_endpoint': self.server_url,
             'ns':OPENID2_NS,
             })

        self.endpoint = OpenIDServiceEndpoint()
        self.endpoint.server_url = self.server_url
        self.endpoint.claimed_id = claimed_id
        self.consumer._checkReturnTo = lambda unused1, unused2 : True

    def tearDown(self):
        CatchLogs.tearDown(self)


    def test_idResMissingNoSigs(self):
        def _vrfy(resp_msg, endpoint=None):
            return endpoint

        self.consumer._verifyDiscoveryResults = _vrfy
        r = self.consumer.complete(self.message, self.endpoint, None)
        self.failUnlessSuccess(r)


    def test_idResNoIdentity(self):
        self.message.delArg(OPENID_NS, 'identity')
        self.message.delArg(OPENID_NS, 'claimed_id')
        self.endpoint.claimed_id = None
        self.message.setArg(OPENID_NS, 'signed', 'return_to,response_nonce,assoc_handle')
        r = self.consumer.complete(self.message, self.endpoint, None)
        self.failUnlessSuccess(r)


    def test_idResMissingIdentitySig(self):
        self.message.setArg(OPENID_NS, 'signed', 'return_to,response_nonce,assoc_handle,claimed_id')
        r = self.consumer.complete(self.message, self.endpoint, None)
        self.failUnlessEqual(r.status, FAILURE)


    def test_idResMissingReturnToSig(self):
        self.message.setArg(OPENID_NS, 'signed', 'identity,response_nonce,assoc_handle,claimed_id')
        r = self.consumer.complete(self.message, self.endpoint, None)
        self.failUnlessEqual(r.status, FAILURE)


    def test_idResMissingAssocHandleSig(self):
        self.message.setArg(OPENID_NS, 'signed', 'identity,response_nonce,return_to,claimed_id')
        r = self.consumer.complete(self.message, self.endpoint, None)
        self.failUnlessEqual(r.status, FAILURE)


    def test_idResMissingClaimedIDSig(self):
        self.message.setArg(OPENID_NS, 'signed', 'identity,response_nonce,return_to,assoc_handle')
        r = self.consumer.complete(self.message, self.endpoint, None)
        self.failUnlessEqual(r.status, FAILURE)


    def failUnlessSuccess(self, response):
        if response.status != SUCCESS:
            self.fail("Non-successful response: %s" % (response,))



class TestCheckAuthResponse(TestIdRes, CatchLogs):
    def setUp(self):
        CatchLogs.setUp(self)
        TestIdRes.setUp(self)

    def tearDown(self):
        CatchLogs.tearDown(self)

    def _createAssoc(self):
        issued = time.time()
        lifetime = 1000
        assoc = association.Association(
            'handle', 'secret', issued, lifetime, 'HMAC-SHA1')
        store = self.consumer.store
        store.storeAssociation(self.server_url, assoc)
        assoc2 = store.getAssociation(self.server_url)
        self.failUnlessEqual(assoc, assoc2)

    def test_goodResponse(self):
        """successful response to check_authentication"""
        response = Message.fromOpenIDArgs({'is_valid':'true',})
        r = self.consumer._processCheckAuthResponse(response, self.server_url)
        self.failUnless(r)

    def test_missingAnswer(self):
        """check_authentication returns false when the server sends no answer"""
        response = Message.fromOpenIDArgs({})
        r = self.consumer._processCheckAuthResponse(response, self.server_url)
        self.failIf(r)

    def test_badResponse(self):
        """check_authentication returns false when is_valid is false"""
        response = Message.fromOpenIDArgs({'is_valid':'false',})
        r = self.consumer._processCheckAuthResponse(response, self.server_url)
        self.failIf(r)

    def test_badResponseInvalidate(self):
        """Make sure that the handle is invalidated when is_valid is false

        From "Verifying directly with the OpenID Provider"::

            If the OP responds with "is_valid" set to "true", and
            "invalidate_handle" is present, the Relying Party SHOULD
            NOT send further authentication requests with that handle.
        """
        self._createAssoc()
        response = Message.fromOpenIDArgs({
            'is_valid':'false',
            'invalidate_handle':'handle',
            })
        r = self.consumer._processCheckAuthResponse(response, self.server_url)
        self.failIf(r)
        self.failUnless(
            self.consumer.store.getAssociation(self.server_url) is None)

    def test_invalidateMissing(self):
        """invalidate_handle with a handle that is not present"""
        response = Message.fromOpenIDArgs({
            'is_valid':'true',
            'invalidate_handle':'missing',
            })
        r = self.consumer._processCheckAuthResponse(response, self.server_url)
        self.failUnless(r)
        self.failUnlessLogMatches(
            'Received "invalidate_handle"'
            )

    def test_invalidateMissing_noStore(self):
        """invalidate_handle with a handle that is not present"""
        response = Message.fromOpenIDArgs({
            'is_valid':'true',
            'invalidate_handle':'missing',
            })
        self.consumer.store = None
        r = self.consumer._processCheckAuthResponse(response, self.server_url)
        self.failUnless(r)
        self.failUnlessLogMatches(
            'Received "invalidate_handle"',
            'Unexpectedly got invalidate_handle without a store')

    def test_invalidatePresent(self):
        """invalidate_handle with a handle that exists

        From "Verifying directly with the OpenID Provider"::

            If the OP responds with "is_valid" set to "true", and
            "invalidate_handle" is present, the Relying Party SHOULD
            NOT send further authentication requests with that handle.
        """
        self._createAssoc()
        response = Message.fromOpenIDArgs({
            'is_valid':'true',
            'invalidate_handle':'handle',
            })
        r = self.consumer._processCheckAuthResponse(response, self.server_url)
        self.failUnless(r)
        self.failUnless(
            self.consumer.store.getAssociation(self.server_url) is None)

class TestSetupNeeded(TestIdRes):
    def failUnlessSetupNeeded(self, expected_setup_url, message):
        try:
            self.consumer._checkSetupNeeded(message)
        except SetupNeededError, why:
            self.failUnlessEqual(expected_setup_url, why.user_setup_url)
        else:
            self.fail("Expected to find an immediate-mode response")

    def test_setupNeededOpenID1(self):
        """The minimum conditions necessary to trigger Setup Needed"""
        setup_url = 'http://unittest/setup-here'
        message = Message.fromPostArgs({
            'openid.mode': 'id_res',
            'openid.user_setup_url': setup_url,
            })
        self.failUnless(message.isOpenID1())
        self.failUnlessSetupNeeded(setup_url, message)

    def test_setupNeededOpenID1_extra(self):
        """Extra stuff along with setup_url still trigger Setup Needed"""
        setup_url = 'http://unittest/setup-here'
        message = Message.fromPostArgs({
            'openid.mode': 'id_res',
            'openid.user_setup_url': setup_url,
            'openid.identity': 'bogus',
            })
        self.failUnless(message.isOpenID1())
        self.failUnlessSetupNeeded(setup_url, message)

    def test_noSetupNeededOpenID1(self):
        """When the user_setup_url is missing on an OpenID 1 message,
        we assume that it's not a cancel response to checkid_immediate"""
        message = Message.fromOpenIDArgs({'mode': 'id_res'})
        self.failUnless(message.isOpenID1())

        # No SetupNeededError raised
        self.consumer._checkSetupNeeded(message)

    def test_setupNeededOpenID2(self):
        message = Message.fromOpenIDArgs({
            'mode':'setup_needed',
            'ns':OPENID2_NS,
            })
        self.failUnless(message.isOpenID2())
        response = self.consumer.complete(message, None, None)
        self.failUnlessEqual('setup_needed', response.status)
        self.failUnlessEqual(None, response.setup_url)

    def test_setupNeededDoesntWorkForOpenID1(self):
        message = Message.fromOpenIDArgs({
            'mode':'setup_needed',
            })

        # No SetupNeededError raised
        self.consumer._checkSetupNeeded(message)

        response = self.consumer.complete(message, None, None)
        self.failUnlessEqual('failure', response.status)
        self.failUnless(response.message.startswith('Invalid openid.mode'))

    def test_noSetupNeededOpenID2(self):
        message = Message.fromOpenIDArgs({
            'mode':'id_res',
            'game':'puerto_rico',
            'ns':OPENID2_NS,
            })
        self.failUnless(message.isOpenID2())

        # No SetupNeededError raised
        self.consumer._checkSetupNeeded(message)

class IdResCheckForFieldsTest(TestIdRes):
    def setUp(self):
        self.consumer = GenericConsumer(None)

    def mkSuccessTest(openid_args, signed_list):
        def test(self):
            message = Message.fromOpenIDArgs(openid_args)
            message.setArg(OPENID_NS, 'signed', ','.join(signed_list))
            self.consumer._idResCheckForFields(message)
        return test

    test_openid1Success = mkSuccessTest(
        {'return_to':'return',
         'assoc_handle':'assoc handle',
         'sig':'a signature',
         'identity':'someone',
         },
        ['return_to', 'identity'])

    test_openid2Success = mkSuccessTest(
        {'ns':OPENID2_NS,
         'return_to':'return',
         'assoc_handle':'assoc handle',
         'sig':'a signature',
         'op_endpoint':'my favourite server',
         'response_nonce':'use only once',
         },
        ['return_to', 'response_nonce', 'assoc_handle'])

    test_openid2Success_identifiers = mkSuccessTest(
        {'ns':OPENID2_NS,
         'return_to':'return',
         'assoc_handle':'assoc handle',
         'sig':'a signature',
         'claimed_id':'i claim to be me',
         'identity':'my server knows me as me',
         'op_endpoint':'my favourite server',
         'response_nonce':'use only once',
         },
        ['return_to', 'response_nonce', 'identity',
         'claimed_id', 'assoc_handle'])

    def mkFailureTest(openid_args, signed_list):
        def test(self):
            message = Message.fromOpenIDArgs(openid_args)
            try:
                self.consumer._idResCheckForFields(message)
            except ProtocolError, why:
                self.failUnless(why[0].startswith('Missing required'))
            else:
                self.fail('Expected an error, but none occurred')
        return test

    test_openid1Missing_returnToSig = mkFailureTest(
        {'return_to':'return',
         'assoc_handle':'assoc handle',
         'sig':'a signature',
         'identity':'someone',
         },
        ['identity'])

    test_openid1Missing_identitySig = mkFailureTest(
        {'return_to':'return',
         'assoc_handle':'assoc handle',
         'sig':'a signature',
         'identity':'someone',
         },
        ['return_to'])

    test_openid1MissingReturnTo = mkFailureTest(
        {'assoc_handle':'assoc handle',
         'sig':'a signature',
         'identity':'someone',
         },
        ['return_to', 'identity'])

    test_openid1MissingAssocHandle = mkFailureTest(
        {'return_to':'return',
         'sig':'a signature',
         'identity':'someone',
         },
        ['return_to', 'identity'])

    # XXX: I could go on...

class CheckAuthHappened(Exception): pass

class CheckNonceVerifyTest(TestIdRes, CatchLogs):
    def setUp(self):
        CatchLogs.setUp(self)
        TestIdRes.setUp(self)
        self.consumer.openid1_nonce_query_arg_name = 'nonce'

    def tearDown(self):
        CatchLogs.tearDown(self)

    def test_openid1Success(self):
        """use consumer-generated nonce"""
        nonce_value = mkNonce()
        self.return_to = 'http://rt.unittest/?nonce=%s' % (nonce_value,)
        self.response = Message.fromOpenIDArgs({'return_to': self.return_to})
        self.response.setArg(BARE_NS, 'nonce', nonce_value)
        self.consumer._idResCheckNonce(self.response, self.endpoint)
        self.failUnlessLogEmpty()

    def test_openid1Missing(self):
        """use consumer-generated nonce"""
        self.response = Message.fromOpenIDArgs({})
        n = self.consumer._idResGetNonceOpenID1(self.response, self.endpoint)
        self.failUnless(n is None, n)
        self.failUnlessLogEmpty()

    def test_consumerNonceOpenID2(self):
        """OpenID 2 does not use consumer-generated nonce"""
        self.return_to = 'http://rt.unittest/?nonce=%s' % (mkNonce(),)
        self.response = Message.fromOpenIDArgs(
            {'return_to': self.return_to, 'ns':OPENID2_NS})
        self.failUnlessRaises(ProtocolError, self.consumer._idResCheckNonce,
                              self.response, self.endpoint)
        self.failUnlessLogEmpty()

    def test_serverNonce(self):
        """use server-generated nonce"""
        self.response = Message.fromOpenIDArgs(
            {'ns':OPENID2_NS, 'response_nonce': mkNonce(),})
        self.consumer._idResCheckNonce(self.response, self.endpoint)
        self.failUnlessLogEmpty()

    def test_serverNonceOpenID1(self):
        """OpenID 1 does not use server-generated nonce"""
        self.response = Message.fromOpenIDArgs(
            {'ns':OPENID1_NS,
             'return_to': 'http://return.to/',
             'response_nonce': mkNonce(),})
        self.failUnlessRaises(ProtocolError, self.consumer._idResCheckNonce,
                              self.response, self.endpoint)
        self.failUnlessLogEmpty()

    def test_badNonce(self):
        """remove the nonce from the store

        From "Checking the Nonce"::

            When the Relying Party checks the signature on an assertion, the

            Relying Party SHOULD ensure that an assertion has not yet
            been accepted with the same value for "openid.response_nonce"
            from the same OP Endpoint URL.
        """
        nonce = mkNonce()
        stamp, salt = splitNonce(nonce)
        self.store.useNonce(self.server_url, stamp, salt)
        self.response = Message.fromOpenIDArgs(
                                  {'response_nonce': nonce,
                                   'ns':OPENID2_NS,
                                   })
        self.failUnlessRaises(ProtocolError, self.consumer._idResCheckNonce,
                              self.response, self.endpoint)

    def test_successWithNoStore(self):
        """When there is no store, checking the nonce succeeds"""
        self.consumer.store = None
        self.response = Message.fromOpenIDArgs(
                                  {'response_nonce': mkNonce(),
                                   'ns':OPENID2_NS,
                                   })
        self.consumer._idResCheckNonce(self.response, self.endpoint)
        self.failUnlessLogEmpty()

    def test_tamperedNonce(self):
        """Malformed nonce"""
        self.response = Message.fromOpenIDArgs(
                                  {'ns':OPENID2_NS,
                                   'response_nonce':'malformed'})
        self.failUnlessRaises(ProtocolError, self.consumer._idResCheckNonce,
                              self.response, self.endpoint)

    def test_missingNonce(self):
        """no nonce parameter on the return_to"""
        self.response = Message.fromOpenIDArgs(
                                  {'return_to': self.return_to})
        self.failUnlessRaises(ProtocolError, self.consumer._idResCheckNonce,
                              self.response, self.endpoint)

class CheckAuthDetectingConsumer(GenericConsumer):
    def _checkAuth(self, *args):
        raise CheckAuthHappened(args)

    def _idResCheckNonce(self, *args):
        """We're not testing nonce-checking, so just return success
        when it asks."""
        return True

class TestCheckAuthTriggered(TestIdRes, CatchLogs):
    consumer_class = CheckAuthDetectingConsumer

    def setUp(self):
        TestIdRes.setUp(self)
        CatchLogs.setUp(self)
        self.disableDiscoveryVerification()

    def test_checkAuthTriggered(self):
        message = Message.fromPostArgs({
            'openid.return_to':self.return_to,
            'openid.identity':self.server_id,
            'openid.assoc_handle':'not_found',
            'openid.sig': GOODSIG,
            'openid.signed': 'identity,return_to',
            })
        self.disableReturnToChecking()
        try:
            result = self.consumer._doIdRes(message, self.endpoint, None)
        except CheckAuthHappened:
            pass
        else:
            self.fail('_checkAuth did not happen. Result was: %r %s' %
                      (result, self.messages))

    def test_checkAuthTriggeredWithAssoc(self):
        # Store an association for this server that does not match the
        # handle that is in the message
        issued = time.time()
        lifetime = 1000
        assoc = association.Association(
            'handle', 'secret', issued, lifetime, 'HMAC-SHA1')
        self.store.storeAssociation(self.server_url, assoc)
        self.disableReturnToChecking()
        message = Message.fromPostArgs({
            'openid.return_to':self.return_to,
            'openid.identity':self.server_id,
            'openid.assoc_handle':'not_found',
            'openid.sig': GOODSIG,
            'openid.signed': 'identity,return_to',
            })
        try:
            result = self.consumer._doIdRes(message, self.endpoint, None)
        except CheckAuthHappened:
            pass
        else:
            self.fail('_checkAuth did not happen. Result was: %r' % (result,))

    def test_expiredAssoc(self):
        # Store an expired association for the server with the handle
        # that is in the message
        issued = time.time() - 10
        lifetime = 0
        handle = 'handle'
        assoc = association.Association(
            handle, 'secret', issued, lifetime, 'HMAC-SHA1')
        self.failUnless(assoc.expiresIn <= 0)
        self.store.storeAssociation(self.server_url, assoc)

        message = Message.fromPostArgs({
            'openid.return_to':self.return_to,
            'openid.identity':self.server_id,
            'openid.assoc_handle':handle,
            'openid.sig': GOODSIG,
            'openid.signed': 'identity,return_to',
            })
        self.disableReturnToChecking()
        self.failUnlessRaises(ProtocolError, self.consumer._doIdRes,
                              message, self.endpoint, None)

    def test_newerAssoc(self):
        lifetime = 1000

        good_issued = time.time() - 10
        good_handle = 'handle'
        good_assoc = association.Association(
            good_handle, 'secret', good_issued, lifetime, 'HMAC-SHA1')
        self.store.storeAssociation(self.server_url, good_assoc)

        bad_issued = time.time() - 5
        bad_handle = 'handle2'
        bad_assoc = association.Association(
            bad_handle, 'secret', bad_issued, lifetime, 'HMAC-SHA1')
        self.store.storeAssociation(self.server_url, bad_assoc)

        query = {
            'return_to':self.return_to,
            'identity':self.server_id,
            'assoc_handle':good_handle,
            }

        message = Message.fromOpenIDArgs(query)
        message = good_assoc.signMessage(message)
        self.disableReturnToChecking()
        info = self.consumer._doIdRes(message, self.endpoint, None)
        self.failUnlessEqual(info.status, SUCCESS, info.message)
        self.failUnlessEqual(self.consumer_id, info.identity_url)



class TestReturnToArgs(unittest.TestCase):
    """Verifying the Return URL paramaters.
    From the specification "Verifying the Return URL"::

        To verify that the "openid.return_to" URL matches the URL that is
        processing this assertion:

         - The URL scheme, authority, and path MUST be the same between the
           two URLs.

         - Any query parameters that are present in the "openid.return_to"
           URL MUST also be present with the same values in the
           accepting URL.

    XXX: So far we have only tested the second item on the list above.
    XXX: _verifyReturnToArgs is not invoked anywhere.
    """

    def setUp(self):
        store = object()
        self.consumer = GenericConsumer(store)

    def test_returnToArgsOkay(self):
        query = {
            'openid.mode': 'id_res',
            'openid.return_to': 'http://example.com/?foo=bar',
            'foo': 'bar',
            }
        # no return value, success is assumed if there are no exceptions.
        self.consumer._verifyReturnToArgs(query)

    def test_returnToArgsUnexpectedArg(self):
        query = {
            'openid.mode': 'id_res',
            'openid.return_to': 'http://example.com/',
            'foo': 'bar',
            }
        # no return value, success is assumed if there are no exceptions.
        self.failUnlessRaises(ProtocolError,
                              self.consumer._verifyReturnToArgs, query)

    def test_returnToMismatch(self):
        query = {
            'openid.mode': 'id_res',
            'openid.return_to': 'http://example.com/?foo=bar',
            }
        # fail, query has no key 'foo'.
        self.failUnlessRaises(ValueError,
                              self.consumer._verifyReturnToArgs, query)

        query['foo'] = 'baz'
        # fail, values for 'foo' do not match.
        self.failUnlessRaises(ValueError,
                              self.consumer._verifyReturnToArgs, query)


    def test_noReturnTo(self):
        query = {'openid.mode': 'id_res'}
        self.failUnlessRaises(ValueError,
                              self.consumer._verifyReturnToArgs, query)

    def test_completeBadReturnTo(self):
        """Test GenericConsumer.complete()'s handling of bad return_to
        values.
        """
        return_to = "http://some.url/path?foo=bar"

        # Scheme, authority, and path differences are checked by
        # GenericConsumer._checkReturnTo.  Query args checked by
        # GenericConsumer._verifyReturnToArgs.
        bad_return_tos = [
            # Scheme only
            "https://some.url/path?foo=bar",
            # Authority only
            "http://some.url.invalid/path?foo=bar",
            # Path only
            "http://some.url/path_extra?foo=bar",
            # Query args differ
            "http://some.url/path?foo=bar2",
            "http://some.url/path?foo2=bar",
            ]

        m = Message(OPENID1_NS)
        m.setArg(OPENID_NS, 'mode', 'cancel')
        m.setArg(BARE_NS, 'foo', 'bar')
        endpoint = None

        for bad in bad_return_tos:
            m.setArg(OPENID_NS, 'return_to', bad)
            self.failIf(self.consumer._checkReturnTo(m, return_to))

    def test_completeGoodReturnTo(self):
        """Test GenericConsumer.complete()'s handling of good
        return_to values.
        """
        return_to = "http://some.url/path"

        good_return_tos = [
            (return_to, {}),
            (return_to + "?another=arg", {(BARE_NS, 'another'): 'arg'}),
            (return_to + "?another=arg#fragment", {(BARE_NS, 'another'): 'arg'}),
            ]

        endpoint = None

        for good, extra in good_return_tos:
            m = Message(OPENID1_NS)
            m.setArg(OPENID_NS, 'mode', 'cancel')

            for ns, key in extra:
                m.setArg(ns, key, extra[(ns, key)])

            m.setArg(OPENID_NS, 'return_to', good)
            result = self.consumer.complete(m, endpoint, return_to)
            self.failUnless(isinstance(result, CancelResponse), \
                            "Expected CancelResponse, got %r for %s" % (result, good,))

class MockFetcher(object):
    def __init__(self, response=None):
        self.response = response or HTTPResponse()
        self.fetches = []

    def fetch(self, url, body=None, headers=None):
        self.fetches.append((url, body, headers))
        return self.response

class ExceptionRaisingMockFetcher(object):
    class MyException(Exception):
        pass

    def fetch(self, url, body=None, headers=None):
        raise self.MyException('mock fetcher exception')

class BadArgCheckingConsumer(GenericConsumer):
    def _makeKVPost(self, args, _):
        assert args == {
            'openid.mode':'check_authentication',
            'openid.signed':'foo',
            }, args
        return None

class TestCheckAuth(unittest.TestCase, CatchLogs):
    consumer_class = GenericConsumer

    def setUp(self):
        CatchLogs.setUp(self)
        self.store = memstore.MemoryStore()

        self.consumer = self.consumer_class(self.store)

        self._orig_fetcher = fetchers.getDefaultFetcher()
        self.fetcher = MockFetcher()
        fetchers.setDefaultFetcher(self.fetcher)

    def tearDown(self):
        CatchLogs.tearDown(self)
        fetchers.setDefaultFetcher(self._orig_fetcher, wrap_exceptions=False)

    def test_error(self):
        self.fetcher.response = HTTPResponse(
            "http://some_url", 404, {'Hea': 'der'}, 'blah:blah\n')
        query = {'openid.signed': 'stuff',
                 'openid.stuff':'a value'}
        r = self.consumer._checkAuth(Message.fromPostArgs(query),
                                     http_server_url)
        self.failIf(r)
        self.failUnless(self.messages)

    def test_bad_args(self):
        query = {
            'openid.signed':'foo',
            'closid.foo':'something',
            }
        consumer = BadArgCheckingConsumer(self.store)
        consumer._checkAuth(Message.fromPostArgs(query), 'does://not.matter')


    def test_signedList(self):
        query = Message.fromOpenIDArgs({
            'mode': 'id_res',
            'ns': OPENID2_NS,
            'sig': 'rabbits',
            'identity': '=example',
            'assoc_handle': 'munchkins',
            'ns.sreg': 'urn:sreg',
            'sreg.email': 'bogus@example.com',
            'signed': 'identity,mode,ns.sreg,sreg.email',
            'foo': 'bar',
            })
        expected = Message.fromOpenIDArgs({
            'mode': 'check_authentication',
            'sig': 'rabbits',
            'assoc_handle': 'munchkins',
            'identity': '=example',
            'signed': 'identity,mode,ns.sreg,sreg.email',
            'ns.sreg': 'urn:sreg',
            'sreg.email': 'bogus@example.com',
            })
        args = self.consumer._createCheckAuthRequest(query)
        self.failUnlessEqual(args.toPostArgs(), expected.toPostArgs())



class TestFetchAssoc(unittest.TestCase, CatchLogs):
    consumer_class = GenericConsumer

    def setUp(self):
        CatchLogs.setUp(self)
        self.store = memstore.MemoryStore()
        self.fetcher = MockFetcher()
        fetchers.setDefaultFetcher(self.fetcher)
        self.consumer = self.consumer_class(self.store)

    def test_error_404(self):
        """404 from a kv post raises HTTPFetchingError"""
        self.fetcher.response = HTTPResponse(
            "http://some_url", 404, {'Hea': 'der'}, 'blah:blah\n')
        self.failUnlessRaises(
            fetchers.HTTPFetchingError,
            self.consumer._makeKVPost,
            Message.fromPostArgs({'mode':'associate'}),
            "http://server_url")

    def test_error_exception_unwrapped(self):
        """Ensure that exceptions are bubbled through from fetchers
        when making associations
        """
        self.fetcher = ExceptionRaisingMockFetcher()
        fetchers.setDefaultFetcher(self.fetcher, wrap_exceptions=False)
        self.failUnlessRaises(self.fetcher.MyException,
                              self.consumer._makeKVPost,
                              Message.fromPostArgs({'mode':'associate'}),
                              "http://server_url")

        # exception fetching returns no association
        e = OpenIDServiceEndpoint()
        e.server_url = 'some://url'
        self.failUnlessRaises(self.fetcher.MyException,
                              self.consumer._getAssociation, e)

        self.failUnlessRaises(self.fetcher.MyException,
                              self.consumer._checkAuth,
                              Message.fromPostArgs({'openid.signed':''}),
                              'some://url')

    def test_error_exception_wrapped(self):
        """Ensure that openid.fetchers.HTTPFetchingError is caught by
        the association creation stuff.
        """
        self.fetcher = ExceptionRaisingMockFetcher()
        # This will wrap exceptions!
        fetchers.setDefaultFetcher(self.fetcher)
        self.failUnlessRaises(fetchers.HTTPFetchingError,
                              self.consumer._makeKVPost,
                              Message.fromOpenIDArgs({'mode':'associate'}),
                              "http://server_url")

        # exception fetching returns no association
        e = OpenIDServiceEndpoint()
        e.server_url = 'some://url'
        self.failUnless(self.consumer._getAssociation(e) is None)

        msg = Message.fromPostArgs({'openid.signed':''})
        self.failIf(self.consumer._checkAuth(msg, 'some://url'))


class TestSuccessResponse(unittest.TestCase):
    def setUp(self):
        self.endpoint = OpenIDServiceEndpoint()
        self.endpoint.claimed_id = 'identity_url'

    def test_extensionResponse(self):
        resp = mkSuccess(self.endpoint, {
            'ns.sreg':'urn:sreg',
            'ns.unittest':'urn:unittest',
            'unittest.one':'1',
            'unittest.two':'2',
            'sreg.nickname':'j3h',
            'return_to':'return_to',
            })
        utargs = resp.extensionResponse('urn:unittest', False)
        self.failUnlessEqual(utargs, {'one':'1', 'two':'2'})
        sregargs = resp.extensionResponse('urn:sreg', False)
        self.failUnlessEqual(sregargs, {'nickname':'j3h'})

    def test_extensionResponseSigned(self):
        args = {
            'ns.sreg':'urn:sreg',
            'ns.unittest':'urn:unittest',
            'unittest.one':'1',
            'unittest.two':'2',
            'sreg.nickname':'j3h',
            'sreg.dob':'yesterday',
            'return_to':'return_to',
            'signed': 'sreg.nickname,unittest.one,sreg.dob',
            }

        signed_list = ['openid.sreg.nickname',
                       'openid.unittest.one',
                       'openid.sreg.dob',]

        # Don't use mkSuccess because it creates an all-inclusive
        # signed list.
        msg = Message.fromOpenIDArgs(args)
        resp = SuccessResponse(self.endpoint, msg, signed_list)

        # All args in this NS are signed, so expect all.
        sregargs = resp.extensionResponse('urn:sreg', True)
        self.failUnlessEqual(sregargs, {'nickname':'j3h', 'dob': 'yesterday'})

        # Not all args in this NS are signed, so expect None when
        # asking for them.
        utargs = resp.extensionResponse('urn:unittest', True)
        self.failUnlessEqual(utargs, None)

    def test_noReturnTo(self):
        resp = mkSuccess(self.endpoint, {})
        self.failUnless(resp.getReturnTo() is None)

    def test_returnTo(self):
        resp = mkSuccess(self.endpoint, {'return_to':'return_to'})
        self.failUnlessEqual(resp.getReturnTo(), 'return_to')

    def test_displayIdentifierClaimedId(self):
        resp = mkSuccess(self.endpoint, {})
        self.failUnlessEqual(resp.getDisplayIdentifier(),
                             resp.endpoint.claimed_id)

    def test_displayIdentifierOverride(self):
        self.endpoint.display_identifier = "http://input.url/"
        resp = mkSuccess(self.endpoint, {})
        self.failUnlessEqual(resp.getDisplayIdentifier(),
                             "http://input.url/")

class StubConsumer(object):
    def __init__(self):
        self.assoc = object()
        self.response = None
        self.endpoint = None

    def begin(self, service):
        auth_req = AuthRequest(service, self.assoc)
        self.endpoint = service
        return auth_req

    def complete(self, message, endpoint, return_to):
        assert endpoint is self.endpoint
        return self.response

class ConsumerTest(unittest.TestCase):
    """Tests for high-level consumer.Consumer functions.

    Its GenericConsumer component is stubbed out with StubConsumer.
    """
    def setUp(self):
        self.endpoint = OpenIDServiceEndpoint()
        self.endpoint.claimed_id = self.identity_url = 'http://identity.url/'
        self.store = None
        self.session = {}
        self.consumer = Consumer(self.session, self.store)
        self.consumer.consumer = StubConsumer()
        self.discovery = Discovery(self.session,
                                   self.identity_url,
                                   self.consumer.session_key_prefix)

    def test_setAssociationPreference(self):
        self.consumer.setAssociationPreference([])
        self.failUnless(isinstance(self.consumer.consumer.negotiator,
                                   association.SessionNegotiator))
        self.failUnlessEqual([],
                             self.consumer.consumer.negotiator.allowed_types)
        self.consumer.setAssociationPreference([('HMAC-SHA1', 'DH-SHA1')])
        self.failUnlessEqual([('HMAC-SHA1', 'DH-SHA1')],
                             self.consumer.consumer.negotiator.allowed_types)

    def withDummyDiscovery(self, callable, dummy_getNextService):
        class DummyDisco(object):
            def __init__(self, *ignored):
                pass

            getNextService = dummy_getNextService

        import openid.consumer.consumer
        old_discovery = openid.consumer.consumer.Discovery
        try:
            openid.consumer.consumer.Discovery = DummyDisco
            callable()
        finally:
            openid.consumer.consumer.Discovery = old_discovery

    def test_beginHTTPError(self):
        """Make sure that the discovery HTTP failure case behaves properly
        """
        def getNextService(self, ignored):
            raise HTTPFetchingError("Unit test")

        def test():
            try:
                self.consumer.begin('unused in this test')
            except DiscoveryFailure, why:
                self.failUnless(why[0].startswith('Error fetching'))
                self.failIf(why[0].find('Unit test') == -1)
            else:
                self.fail('Expected DiscoveryFailure')

        self.withDummyDiscovery(test, getNextService)

    def test_beginNoServices(self):
        def getNextService(self, ignored):
            return None

        url = 'http://a.user.url/'
        def test():
            try:
                self.consumer.begin(url)
            except DiscoveryFailure, why:
                self.failUnless(why[0].startswith('No usable OpenID'))
                self.failIf(why[0].find(url) == -1)
            else:
                self.fail('Expected DiscoveryFailure')

        self.withDummyDiscovery(test, getNextService)


    def test_beginWithoutDiscovery(self):
        # Does this really test anything non-trivial?
        result = self.consumer.beginWithoutDiscovery(self.endpoint)

        # The result is an auth request
        self.failUnless(isinstance(result, AuthRequest))

        # Side-effect of calling beginWithoutDiscovery is setting the
        # session value to the endpoint attribute of the result
        self.failUnless(self.session[self.consumer._token_key] is result.endpoint)

        # The endpoint that we passed in is the endpoint on the auth_request
        self.failUnless(result.endpoint is self.endpoint)

    def test_completeEmptySession(self):
        text = "failed complete"

        def checkEndpoint(message, endpoint, return_to):
            self.failUnless(endpoint is None)
            return FailureResponse(endpoint, text)

        self.consumer.consumer.complete = checkEndpoint

        response = self.consumer.complete({}, None)
        self.failUnlessEqual(response.status, FAILURE)
        self.failUnlessEqual(response.message, text)
        self.failUnless(response.identity_url is None)

    def _doResp(self, auth_req, exp_resp):
        """complete a transaction, using the expected response from
        the generic consumer."""
        # response is an attribute of StubConsumer, returned by
        # StubConsumer.complete.
        self.consumer.consumer.response = exp_resp

        # endpoint is stored in the session
        self.failUnless(self.session)
        resp = self.consumer.complete({}, None)

        # All responses should have the same identity URL, and the
        # session should be cleaned out
        if self.endpoint.claimed_id != IDENTIFIER_SELECT:
            self.failUnless(resp.identity_url is self.identity_url)

        self.failIf(self.consumer._token_key in self.session)

        # Expected status response
        self.failUnlessEqual(resp.status, exp_resp.status)

        return resp

    def _doRespNoDisco(self, exp_resp):
        """Set up a transaction without discovery"""
        auth_req = self.consumer.beginWithoutDiscovery(self.endpoint)
        resp = self._doResp(auth_req, exp_resp)
        # There should be nothing left in the session once we have completed.
        self.failIf(self.session)
        return resp

    def test_noDiscoCompleteSuccessWithToken(self):
        self._doRespNoDisco(mkSuccess(self.endpoint, {}))

    def test_noDiscoCompleteCancelWithToken(self):
        self._doRespNoDisco(CancelResponse(self.endpoint))

    def test_noDiscoCompleteFailure(self):
        msg = 'failed!'
        resp = self._doRespNoDisco(FailureResponse(self.endpoint, msg))
        self.failUnless(resp.message is msg)

    def test_noDiscoCompleteSetupNeeded(self):
        setup_url = 'http://setup.url/'
        resp = self._doRespNoDisco(
            SetupNeededResponse(self.endpoint, setup_url))
        self.failUnless(resp.setup_url is setup_url)

    # To test that discovery is cleaned up, we need to initialize a
    # Yadis manager, and have it put its values in the session.
    def _doRespDisco(self, is_clean, exp_resp):
        """Set up and execute a transaction, with discovery"""
        self.discovery.createManager([self.endpoint], self.identity_url)
        auth_req = self.consumer.begin(self.identity_url)
        resp = self._doResp(auth_req, exp_resp)

        manager = self.discovery.getManager()
        if is_clean:
            self.failUnless(self.discovery.getManager() is None, manager)
        else:
            self.failIf(self.discovery.getManager() is None, manager)

        return resp

    # Cancel and success DO clean up the discovery process
    def test_completeSuccess(self):
        self._doRespDisco(True, mkSuccess(self.endpoint, {}))

    def test_completeCancel(self):
        self._doRespDisco(True, CancelResponse(self.endpoint))

    # Failure and setup_needed don't clean up the discovery process
    def test_completeFailure(self):
        msg = 'failed!'
        resp = self._doRespDisco(False, FailureResponse(self.endpoint, msg))
        self.failUnless(resp.message is msg)

    def test_completeSetupNeeded(self):
        setup_url = 'http://setup.url/'
        resp = self._doRespDisco(
            False,
            SetupNeededResponse(self.endpoint, setup_url))
        self.failUnless(resp.setup_url is setup_url)

    def test_successDifferentURL(self):
        """
        Be sure that the session gets cleaned up when the response is
        successful and has a different URL than the one in the
        request.
        """
        # Set up a request endpoint describing an IDP URL
        self.identity_url = 'http://idp.url/'
        self.endpoint.claimed_id = self.endpoint.local_id = IDENTIFIER_SELECT

        # Use a response endpoint with a different URL (asserted by
        # the IDP)
        resp_endpoint = OpenIDServiceEndpoint()
        resp_endpoint.claimed_id = "http://user.url/"

        resp = self._doRespDisco(
            True,
            mkSuccess(resp_endpoint, {}))
        self.failUnless(self.discovery.getManager(force=True) is None)

    def test_begin(self):
        self.discovery.createManager([self.endpoint], self.identity_url)
        # Should not raise an exception
        auth_req = self.consumer.begin(self.identity_url)
        self.failUnless(isinstance(auth_req, AuthRequest))
        self.failUnless(auth_req.endpoint is self.endpoint)
        self.failUnless(auth_req.endpoint is self.consumer.consumer.endpoint)
        self.failUnless(auth_req.assoc is self.consumer.consumer.assoc)



class IDPDrivenTest(unittest.TestCase):

    def setUp(self):
        self.store = GoodAssocStore()
        self.consumer = GenericConsumer(self.store)
        self.endpoint = OpenIDServiceEndpoint()
        self.endpoint.server_url = "http://idp.unittest/"


    def test_idpDrivenBegin(self):
        # Testing here that the token-handling doesn't explode...
        self.consumer.begin(self.endpoint)


    def test_idpDrivenComplete(self):
        identifier = '=directed_identifier'
        message = Message.fromPostArgs({
            'openid.identity': '=directed_identifier',
            'openid.return_to': 'x',
            'openid.assoc_handle': 'z',
            'openid.signed': 'identity,return_to',
            'openid.sig': GOODSIG,
            })

        discovered_endpoint = OpenIDServiceEndpoint()
        discovered_endpoint.claimed_id = identifier
        discovered_endpoint.server_url = self.endpoint.server_url
        discovered_endpoint.local_id = identifier
        iverified = []
        def verifyDiscoveryResults(identifier, endpoint):
            self.failUnless(endpoint is self.endpoint)
            iverified.append(discovered_endpoint)
            return discovered_endpoint
        self.consumer._verifyDiscoveryResults = verifyDiscoveryResults
        self.consumer._idResCheckNonce = lambda *args: True
        self.consumer._checkReturnTo = lambda unused1, unused2 : True
        response = self.consumer._doIdRes(message, self.endpoint, None)

        self.failUnlessSuccess(response)
        self.failUnlessEqual(response.identity_url, "=directed_identifier")

        # assert that discovery attempt happens and returns good
        self.failUnlessEqual(iverified, [discovered_endpoint])


    def test_idpDrivenCompleteFraud(self):
        # crap with an identifier that doesn't match discovery info
        message = Message.fromPostArgs({
            'openid.identity': '=directed_identifier',
            'openid.return_to': 'x',
            'openid.assoc_handle': 'z',
            'openid.signed': 'identity,return_to',
            'openid.sig': GOODSIG,
            })
        def verifyDiscoveryResults(identifier, endpoint):
            raise DiscoveryFailure("PHREAK!", None)
        self.consumer._verifyDiscoveryResults = verifyDiscoveryResults
        self.consumer._checkReturnTo = lambda unused1, unused2 : True
        self.failUnlessRaises(DiscoveryFailure, self.consumer._doIdRes,
                              message, self.endpoint, None)


    def failUnlessSuccess(self, response):
        if response.status != SUCCESS:
            self.fail("Non-successful response: %s" % (response,))



class TestDiscoveryVerification(unittest.TestCase):
    services = []

    def setUp(self):
        self.store = GoodAssocStore()
        self.consumer = GenericConsumer(self.store)

        self.consumer._discover = self.discoveryFunc

        self.identifier = "http://idp.unittest/1337"
        self.server_url = "http://endpoint.unittest/"

        self.message = Message.fromPostArgs({
            'openid.ns': OPENID2_NS,
            'openid.identity': self.identifier,
            'openid.claimed_id': self.identifier,
            'openid.op_endpoint': self.server_url,
            })

        self.endpoint = OpenIDServiceEndpoint()
        self.endpoint.server_url = self.server_url

    def test_theGoodStuff(self):
        endpoint = OpenIDServiceEndpoint()
        endpoint.type_uris = [OPENID_2_0_TYPE]
        endpoint.claimed_id = self.identifier
        endpoint.server_url = self.server_url
        endpoint.local_id = self.identifier
        self.services = [endpoint]
        r = self.consumer._verifyDiscoveryResults(self.message, endpoint)

        self.failUnlessEqual(r, endpoint)


    def test_otherServer(self):
        text = "verify failed"

        def discoverAndVerify(to_match):
            self.failUnlessEqual(self.identifier, to_match.claimed_id)
            raise ProtocolError(text)

        self.consumer._discoverAndVerify = discoverAndVerify

        # a set of things without the stuff
        endpoint = OpenIDServiceEndpoint()
        endpoint.type_uris = [OPENID_2_0_TYPE]
        endpoint.claimed_id = self.identifier
        endpoint.server_url = "http://the-MOON.unittest/"
        endpoint.local_id = self.identifier
        self.services = [endpoint]
        try:
            r = self.consumer._verifyDiscoveryResults(self.message, endpoint)
        except ProtocolError, e:
            # Should we make more ProtocolError subclasses?
            self.failUnless(str(e), text)
        else:
            self.fail("expected ProtocolError, %r returned." % (r,))
            

    def test_foreignDelegate(self):
        text = "verify failed"

        def discoverAndVerify(to_match):
            self.failUnlessEqual(self.identifier, to_match.claimed_id)
            raise ProtocolError(text)

        self.consumer._discoverAndVerify = discoverAndVerify

        # a set of things with the server stuff but other delegate
        endpoint = OpenIDServiceEndpoint()
        endpoint.type_uris = [OPENID_2_0_TYPE]
        endpoint.claimed_id = self.identifier
        endpoint.server_url = self.server_url
        endpoint.local_id = "http://unittest/juan-carlos"

        try:
            r = self.consumer._verifyDiscoveryResults(self.message, endpoint)
        except ProtocolError, e:
            self.failUnlessEqual(str(e), text)
        else:
            self.fail("Exepected ProtocolError, %r returned" % (r,))

    def test_nothingDiscovered(self):
        # a set of no things.
        self.services = []
        self.failUnlessRaises(DiscoveryFailure,
                              self.consumer._verifyDiscoveryResults,
                              self.message, self.endpoint)


    def discoveryFunc(self, identifier):
        return identifier, self.services


class TestCreateAssociationRequest(unittest.TestCase):
    def setUp(self):
        class DummyEndpoint(object):
            use_compatibility = False

            def compatibilityMode(self):
                return self.use_compatibility

        self.endpoint = DummyEndpoint()
        self.consumer = GenericConsumer(store=None)
        self.assoc_type = 'HMAC-SHA1'

    def test_noEncryptionSendsType(self):
        session_type = 'no-encryption'
        session, args = self.consumer._createAssociateRequest(
            self.endpoint, self.assoc_type, session_type)

        self.failUnless(isinstance(session, PlainTextConsumerSession))
        expected = Message.fromOpenIDArgs(
            {'ns':OPENID2_NS,
             'session_type':session_type,
             'mode':'associate',
             'assoc_type':self.assoc_type,
             })

        self.failUnlessEqual(expected, args)

    def test_noEncryptionCompatibility(self):
        self.endpoint.use_compatibility = True
        session_type = 'no-encryption'
        session, args = self.consumer._createAssociateRequest(
            self.endpoint, self.assoc_type, session_type)

        self.failUnless(isinstance(session, PlainTextConsumerSession))
        self.failUnlessEqual(Message.fromOpenIDArgs({'mode':'associate',
                              'assoc_type':self.assoc_type,
                              }), args)

    def test_dhSHA1Compatibility(self):
        # Set the consumer's session type to a fast session since we
        # need it here.
        setConsumerSession(self.consumer)

        self.endpoint.use_compatibility = True
        session_type = 'DH-SHA1'
        session, args = self.consumer._createAssociateRequest(
            self.endpoint, self.assoc_type, session_type)

        self.failUnless(isinstance(session, DiffieHellmanSHA1ConsumerSession))

        # This is a random base-64 value, so just check that it's
        # present.
        self.failUnless(args.getArg(OPENID1_NS, 'dh_consumer_public'))
        args.delArg(OPENID1_NS, 'dh_consumer_public')

        # OK, session_type is set here and not for no-encryption
        # compatibility
        expected = Message.fromOpenIDArgs({'mode':'associate',
                                           'session_type':'DH-SHA1',
                                           'assoc_type':self.assoc_type,
                                           'dh_modulus': 'BfvStQ==',
                                           'dh_gen': 'Ag==',
                                           })

        self.failUnlessEqual(expected, args)

    # XXX: test the other types

class TestDiffieHellmanResponseParameters(object):
    session_cls = None
    message_namespace = None

    def setUp(self):
        # Pre-compute DH with small prime so tests run quickly.
        self.server_dh = DiffieHellman(100389557, 2)
        self.consumer_dh = DiffieHellman(100389557, 2)

        # base64(btwoc(g ^ xb mod p))
        self.dh_server_public = cryptutil.longToBase64(self.server_dh.public)

        self.secret = cryptutil.randomString(self.session_cls.secret_size)

        self.enc_mac_key = oidutil.toBase64(
            self.server_dh.xorSecret(self.consumer_dh.public,
                                     self.secret,
                                     self.session_cls.hash_func))

        self.consumer_session = self.session_cls(self.consumer_dh)

        self.msg = Message(self.message_namespace)

    def testExtractSecret(self):
        self.msg.setArg(OPENID_NS, 'dh_server_public', self.dh_server_public)
        self.msg.setArg(OPENID_NS, 'enc_mac_key', self.enc_mac_key)

        extracted = self.consumer_session.extractSecret(self.msg)
        self.failUnlessEqual(extracted, self.secret)

    def testAbsentServerPublic(self):
        self.msg.setArg(OPENID_NS, 'enc_mac_key', self.enc_mac_key)

        self.failUnlessRaises(KeyError, self.consumer_session.extractSecret, self.msg)

    def testAbsentMacKey(self):
        self.msg.setArg(OPENID_NS, 'dh_server_public', self.dh_server_public)

        self.failUnlessRaises(KeyError, self.consumer_session.extractSecret, self.msg)

    def testInvalidBase64Public(self):
        self.msg.setArg(OPENID_NS, 'dh_server_public', 'n o t b a s e 6 4.')
        self.msg.setArg(OPENID_NS, 'enc_mac_key', self.enc_mac_key)

        self.failUnlessRaises(ValueError, self.consumer_session.extractSecret, self.msg)

    def testInvalidBase64MacKey(self):
        self.msg.setArg(OPENID_NS, 'dh_server_public', self.dh_server_public)
        self.msg.setArg(OPENID_NS, 'enc_mac_key', 'n o t base 64')

        self.failUnlessRaises(ValueError, self.consumer_session.extractSecret, self.msg)

class TestOpenID1SHA1(TestDiffieHellmanResponseParameters, unittest.TestCase):
    session_cls = DiffieHellmanSHA1ConsumerSession
    message_namespace = OPENID1_NS

class TestOpenID2SHA1(TestDiffieHellmanResponseParameters, unittest.TestCase):
    session_cls = DiffieHellmanSHA1ConsumerSession
    message_namespace = OPENID2_NS

if cryptutil.SHA256_AVAILABLE:
    class TestOpenID2SHA256(TestDiffieHellmanResponseParameters, unittest.TestCase):
        session_cls = DiffieHellmanSHA256ConsumerSession
        message_namespace = OPENID2_NS
else:
    warnings.warn("Not running SHA256 association session tests.")

class TestNoStore(unittest.TestCase):
    def setUp(self):
        self.consumer = GenericConsumer(None)

    def test_completeNoGetAssoc(self):
        """_getAssociation is never called when the store is None"""
        def notCalled(unused):
            self.fail('This method was unexpectedly called')

        endpoint = OpenIDServiceEndpoint()
        endpoint.claimed_id = 'identity_url'

        self.consumer._getAssociation = notCalled
        auth_request = self.consumer.begin(endpoint)
        # _getAssociation was not called




class NonAnonymousAuthRequest(object):
    endpoint = 'unused'

    def setAnonymous(self, unused):
        raise ValueError('Should trigger ProtocolError')

class TestConsumerAnonymous(unittest.TestCase):
    def test_beginWithoutDiscoveryAnonymousFail(self):
        """Make sure that ValueError for setting an auth request
        anonymous gets converted to a ProtocolError
        """
        sess = {}
        consumer = Consumer(sess, None)
        def bogusBegin(unused):
            return NonAnonymousAuthRequest()
        consumer.consumer.begin = bogusBegin
        self.failUnlessRaises(
            ProtocolError,
            consumer.beginWithoutDiscovery, None)


class TestDiscoverAndVerify(unittest.TestCase):
    def setUp(self):
        self.consumer = GenericConsumer(None)
        self.discovery_result = None
        def dummyDiscover(unused_identifier):
            return self.discovery_result
        self.consumer._discover = dummyDiscover
        self.to_match = OpenIDServiceEndpoint()

    def failUnlessDiscoveryFailure(self):
        self.failUnlessRaises(
            DiscoveryFailure,
            self.consumer._discoverAndVerify, self.to_match)

    def test_noServices(self):
        """Discovery returning no results results in a
        DiscoveryFailure exception"""
        self.discovery_result = (None, [])
        self.failUnlessDiscoveryFailure()

    def test_noMatches(self):
        """If no discovered endpoint matches the values from the
        assertion, then we end up raising a ProtocolError
        """
        self.discovery_result = (None, ['unused'])
        def raiseProtocolError(unused1, unused2):
            raise ProtocolError('unit test')
        self.consumer._verifyDiscoverySingle = raiseProtocolError
        self.failUnlessDiscoveryFailure()

    def test_matches(self):
        """If an endpoint matches, we return it
        """
        # Discovery returns a single "endpoint" object
        matching_endpoint = 'matching endpoint'
        self.discovery_result = (None, [matching_endpoint])

        # Make verifying discovery return True for this endpoint
        def returnTrue(unused1, unused2):
            return True
        self.consumer._verifyDiscoverySingle = returnTrue

        # Since _verifyDiscoverySingle returns True, we should get the
        # first endpoint that we passed in as a result.
        result = self.consumer._discoverAndVerify(self.to_match)
        self.failUnlessEqual(matching_endpoint, result)

from openid.extension import Extension
class SillyExtension(Extension):
    ns_uri = 'http://silly.example.com/'
    ns_alias = 'silly'

    def getExtensionArgs(self):
        return {'i_am':'silly'}

class TestAddExtension(unittest.TestCase):

    def test_SillyExtension(self):
        ext = SillyExtension()
        ar = AuthRequest(OpenIDServiceEndpoint(), None)
        ar.addExtension(ext)
        ext_args = ar.message.getArgs(ext.ns_uri)
        self.failUnlessEqual(ext.getExtensionArgs(), ext_args)



class TestKVPost(unittest.TestCase):
    def setUp(self):
        self.server_url = 'http://unittest/%s' % (self.id(),)

    def test_200(self):
        from openid.fetchers import HTTPResponse
        response = HTTPResponse()
        response.status = 200
        response.body = "foo:bar\nbaz:quux\n"
        r = _httpResponseToMessage(response, self.server_url)
        expected_msg = Message.fromOpenIDArgs({'foo':'bar','baz':'quux'})
        self.failUnlessEqual(expected_msg, r)


    def test_400(self):
        response = HTTPResponse()
        response.status = 400
        response.body = "error:bonk\nerror_code:7\n"
        try:
            r = _httpResponseToMessage(response, self.server_url)
        except ServerError, e:
            self.failUnlessEqual(e.error_text, 'bonk')
            self.failUnlessEqual(e.error_code, '7')
        else:
            self.fail("Expected ServerError, got return %r" % (r,))


    def test_500(self):
        # 500 as an example of any non-200, non-400 code.
        response = HTTPResponse()
        response.status = 500
        response.body = "foo:bar\nbaz:quux\n"
        self.failUnlessRaises(fetchers.HTTPFetchingError,
                              _httpResponseToMessage, response,
                              self.server_url)




if __name__ == '__main__':
    unittest.main()
