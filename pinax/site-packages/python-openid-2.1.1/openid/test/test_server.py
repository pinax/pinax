"""Tests for openid.server.
"""
from openid.server import server
from openid import association, cryptutil, oidutil
from openid.message import Message, OPENID_NS, OPENID2_NS, OPENID1_NS, \
     IDENTIFIER_SELECT, no_default, OPENID1_URL_LIMIT
from openid.store import memstore
import cgi

import unittest
import warnings

from urlparse import urlparse

# In general, if you edit or add tests here, try to move in the direction
# of testing smaller units.  For testing the external interfaces, we'll be
# developing an implementation-agnostic testing suite.

# for more, see /etc/ssh/moduli

ALT_MODULUS = 0xCAADDDEC1667FC68B5FA15D53C4E1532DD24561A1A2D47A12C01ABEA1E00731F6921AAC40742311FDF9E634BB7131BEE1AF240261554389A910425E044E88C8359B010F5AD2B80E29CB1A5B027B19D9E01A6F63A6F45E5D7ED2FF6A2A0085050A7D0CF307C3DB51D2490355907B4427C23A98DF1EB8ABEF2BA209BB7AFFE86A7
ALT_GEN = 5

class CatchLogs(object):
    def setUp(self):
        self.old_logger = oidutil.log
        oidutil.log = self.gotLogMessage
        self.messages = []

    def gotLogMessage(self, message):
        self.messages.append(message)

    def tearDown(self):
        oidutil.log = self.old_logger

class TestProtocolError(unittest.TestCase):
    def test_browserWithReturnTo(self):
        return_to = "http://rp.unittest/consumer"
        # will be a ProtocolError raised by Decode or CheckIDRequest.answer
        args = Message.fromPostArgs({
            'openid.mode': 'monkeydance',
            'openid.identity': 'http://wagu.unittest/',
            'openid.return_to': return_to,
            })
        e = server.ProtocolError(args, "plucky")
        self.failUnless(e.hasReturnTo())
        expected_args = {
            'openid.mode': ['error'],
            'openid.error': ['plucky'],
            }

        rt_base, result_args = e.encodeToURL().split('?', 1)
        result_args = cgi.parse_qs(result_args)
        self.failUnlessEqual(result_args, expected_args)

    def test_browserWithReturnTo_OpenID2_GET(self):
        return_to = "http://rp.unittest/consumer"
        # will be a ProtocolError raised by Decode or CheckIDRequest.answer
        args = Message.fromPostArgs({
            'openid.ns': OPENID2_NS,
            'openid.mode': 'monkeydance',
            'openid.identity': 'http://wagu.unittest/',
            'openid.claimed_id': 'http://wagu.unittest/',
            'openid.return_to': return_to,
            })
        e = server.ProtocolError(args, "plucky")
        self.failUnless(e.hasReturnTo())
        expected_args = {
            'openid.ns': [OPENID2_NS],
            'openid.mode': ['error'],
            'openid.error': ['plucky'],
            }

        rt_base, result_args = e.encodeToURL().split('?', 1)
        result_args = cgi.parse_qs(result_args)
        self.failUnlessEqual(result_args, expected_args)

    def test_browserWithReturnTo_OpenID2_POST(self):
        return_to = "http://rp.unittest/consumer" + ('x' * OPENID1_URL_LIMIT)
        # will be a ProtocolError raised by Decode or CheckIDRequest.answer
        args = Message.fromPostArgs({
            'openid.ns': OPENID2_NS,
            'openid.mode': 'monkeydance',
            'openid.identity': 'http://wagu.unittest/',
            'openid.claimed_id': 'http://wagu.unittest/',
            'openid.return_to': return_to,
            })
        e = server.ProtocolError(args, "plucky")
        self.failUnless(e.hasReturnTo())
        expected_args = {
            'openid.ns': [OPENID2_NS],
            'openid.mode': ['error'],
            'openid.error': ['plucky'],
            }

        self.failUnless(e.whichEncoding() == server.ENCODE_HTML_FORM)
        self.failUnless(e.toFormMarkup() == e.toMessage().toFormMarkup(
            args.getArg(OPENID_NS, 'return_to')))

    def test_browserWithReturnTo_OpenID1_exceeds_limit(self):
        return_to = "http://rp.unittest/consumer" + ('x' * OPENID1_URL_LIMIT)
        # will be a ProtocolError raised by Decode or CheckIDRequest.answer
        args = Message.fromPostArgs({
            'openid.mode': 'monkeydance',
            'openid.identity': 'http://wagu.unittest/',
            'openid.return_to': return_to,
            })
        e = server.ProtocolError(args, "plucky")
        self.failUnless(e.hasReturnTo())
        expected_args = {
            'openid.mode': ['error'],
            'openid.error': ['plucky'],
            }

        self.failUnless(e.whichEncoding() == server.ENCODE_URL)

        rt_base, result_args = e.encodeToURL().split('?', 1)
        result_args = cgi.parse_qs(result_args)
        self.failUnlessEqual(result_args, expected_args)

    def test_noReturnTo(self):
        # will be a ProtocolError raised by Decode or CheckIDRequest.answer
        args = Message.fromPostArgs({
            'openid.mode': 'zebradance',
            'openid.identity': 'http://wagu.unittest/',
            })
        e = server.ProtocolError(args, "waffles")
        self.failIf(e.hasReturnTo())
        expected = """error:waffles
mode:error
"""
        self.failUnlessEqual(e.encodeToKVForm(), expected)



class TestDecode(unittest.TestCase):
    def setUp(self):
        self.claimed_id = 'http://de.legating.de.coder.unittest/'
        self.id_url = "http://decoder.am.unittest/"
        self.rt_url = "http://rp.unittest/foobot/?qux=zam"
        self.tr_url = "http://rp.unittest/"
        self.assoc_handle = "{assoc}{handle}"
        self.op_endpoint = 'http://endpoint.unittest/encode'
        self.store = memstore.MemoryStore()
        self.server = server.Server(self.store, self.op_endpoint)
        self.decode = self.server.decoder.decode
        self.decode = server.Decoder(self.server).decode

    def test_none(self):
        args = {}
        r = self.decode(args)
        self.failUnlessEqual(r, None)

    def test_irrelevant(self):
        args = {
            'pony': 'spotted',
            'sreg.mutant_power': 'decaffinator',
            }
        self.failUnlessRaises(server.ProtocolError, self.decode, args)

    def test_bad(self):
        args = {
            'openid.mode': 'twos-compliment',
            'openid.pants': 'zippered',
            }
        self.failUnlessRaises(server.ProtocolError, self.decode, args)

    def test_dictOfLists(self):
        args = {
            'openid.mode': ['checkid_setup'],
            'openid.identity': self.id_url,
            'openid.assoc_handle': self.assoc_handle,
            'openid.return_to': self.rt_url,
            'openid.trust_root': self.tr_url,
            }
        try:
            result = self.decode(args)
        except TypeError, err:
            self.failUnless(str(err).find('values') != -1, err)
        else:
            self.fail("Expected TypeError, but got result %s" % (result,))

    def test_checkidImmediate(self):
        args = {
            'openid.mode': 'checkid_immediate',
            'openid.identity': self.id_url,
            'openid.assoc_handle': self.assoc_handle,
            'openid.return_to': self.rt_url,
            'openid.trust_root': self.tr_url,
            # should be ignored
            'openid.some.extension': 'junk',
            }
        r = self.decode(args)
        self.failUnless(isinstance(r, server.CheckIDRequest))
        self.failUnlessEqual(r.mode, "checkid_immediate")
        self.failUnlessEqual(r.immediate, True)
        self.failUnlessEqual(r.identity, self.id_url)
        self.failUnlessEqual(r.trust_root, self.tr_url)
        self.failUnlessEqual(r.return_to, self.rt_url)
        self.failUnlessEqual(r.assoc_handle, self.assoc_handle)

    def test_checkidSetup(self):
        args = {
            'openid.mode': 'checkid_setup',
            'openid.identity': self.id_url,
            'openid.assoc_handle': self.assoc_handle,
            'openid.return_to': self.rt_url,
            'openid.trust_root': self.tr_url,
            }
        r = self.decode(args)
        self.failUnless(isinstance(r, server.CheckIDRequest))
        self.failUnlessEqual(r.mode, "checkid_setup")
        self.failUnlessEqual(r.immediate, False)
        self.failUnlessEqual(r.identity, self.id_url)
        self.failUnlessEqual(r.trust_root, self.tr_url)
        self.failUnlessEqual(r.return_to, self.rt_url)

    def test_checkidSetupOpenID2(self):
        args = {
            'openid.ns': OPENID2_NS,
            'openid.mode': 'checkid_setup',
            'openid.identity': self.id_url,
            'openid.claimed_id': self.claimed_id,
            'openid.assoc_handle': self.assoc_handle,
            'openid.return_to': self.rt_url,
            'openid.realm': self.tr_url,
            }
        r = self.decode(args)
        self.failUnless(isinstance(r, server.CheckIDRequest))
        self.failUnlessEqual(r.mode, "checkid_setup")
        self.failUnlessEqual(r.immediate, False)
        self.failUnlessEqual(r.identity, self.id_url)
        self.failUnlessEqual(r.claimed_id, self.claimed_id)
        self.failUnlessEqual(r.trust_root, self.tr_url)
        self.failUnlessEqual(r.return_to, self.rt_url)

    def test_checkidSetupNoClaimedIDOpenID2(self):
        args = {
            'openid.ns': OPENID2_NS,
            'openid.mode': 'checkid_setup',
            'openid.identity': self.id_url,
            'openid.assoc_handle': self.assoc_handle,
            'openid.return_to': self.rt_url,
            'openid.realm': self.tr_url,
            }
        self.failUnlessRaises(server.ProtocolError, self.decode, args)

    def test_checkidSetupNoIdentityOpenID2(self):
        args = {
            'openid.ns': OPENID2_NS,
            'openid.mode': 'checkid_setup',
            'openid.assoc_handle': self.assoc_handle,
            'openid.return_to': self.rt_url,
            'openid.realm': self.tr_url,
            }
        r = self.decode(args)
        self.failUnless(isinstance(r, server.CheckIDRequest))
        self.failUnlessEqual(r.mode, "checkid_setup")
        self.failUnlessEqual(r.immediate, False)
        self.failUnlessEqual(r.identity, None)
        self.failUnlessEqual(r.trust_root, self.tr_url)
        self.failUnlessEqual(r.return_to, self.rt_url)

    def test_checkidSetupNoReturnOpenID1(self):
        """Make sure an OpenID 1 request cannot be decoded if it lacks
        a return_to.
        """
        args = {
            'openid.mode': 'checkid_setup',
            'openid.identity': self.id_url,
            'openid.assoc_handle': self.assoc_handle,
            'openid.trust_root': self.tr_url,
            }
        self.failUnlessRaises(server.ProtocolError, self.decode, args)

    def test_checkidSetupNoReturnOpenID2(self):
        """Make sure an OpenID 2 request with no return_to can be
        decoded, and make sure a response to such a request raises
        NoReturnToError.
        """
        args = {
            'openid.ns': OPENID2_NS,
            'openid.mode': 'checkid_setup',
            'openid.identity': self.id_url,
            'openid.claimed_id': self.id_url,
            'openid.assoc_handle': self.assoc_handle,
            'openid.realm': self.tr_url,
            }
        self.failUnless(isinstance(self.decode(args), server.CheckIDRequest))

        req = self.decode(args)
        self.assertRaises(server.NoReturnToError, req.answer, False)
        self.assertRaises(server.NoReturnToError, req.encodeToURL, 'bogus')
        self.assertRaises(server.NoReturnToError, req.getCancelURL)

    def test_checkidSetupRealmRequiredOpenID2(self):
        """Make sure that an OpenID 2 request which lacks return_to
        cannot be decoded if it lacks a realm.  Spec: This value
        (openid.realm) MUST be sent if openid.return_to is omitted.
        """
        args = {
            'openid.ns': OPENID2_NS,
            'openid.mode': 'checkid_setup',
            'openid.identity': self.id_url,
            'openid.assoc_handle': self.assoc_handle,
            }
        self.failUnlessRaises(server.ProtocolError, self.decode, args)

    def test_checkidSetupBadReturn(self):
        args = {
            'openid.mode': 'checkid_setup',
            'openid.identity': self.id_url,
            'openid.assoc_handle': self.assoc_handle,
            'openid.return_to': 'not a url',
            }
        try:
            result = self.decode(args)
        except server.ProtocolError, err:
            self.failUnless(err.openid_message)
        else:
            self.fail("Expected ProtocolError, instead returned with %s" %
                      (result,))

    def test_checkidSetupUntrustedReturn(self):
        args = {
            'openid.mode': 'checkid_setup',
            'openid.identity': self.id_url,
            'openid.assoc_handle': self.assoc_handle,
            'openid.return_to': self.rt_url,
            'openid.trust_root': 'http://not-the-return-place.unittest/',
            }
        try:
            result = self.decode(args)
        except server.UntrustedReturnURL, err:
            self.failUnless(err.openid_message)
        else:
            self.fail("Expected UntrustedReturnURL, instead returned with %s" %
                      (result,))

    def test_checkAuth(self):
        args = {
            'openid.mode': 'check_authentication',
            'openid.assoc_handle': '{dumb}{handle}',
            'openid.sig': 'sigblob',
            'openid.signed': 'identity,return_to,response_nonce,mode',
            'openid.identity': 'signedval1',
            'openid.return_to': 'signedval2',
            'openid.response_nonce': 'signedval3',
            'openid.baz': 'unsigned',
            }
        r = self.decode(args)
        self.failUnless(isinstance(r, server.CheckAuthRequest))
        self.failUnlessEqual(r.mode, 'check_authentication')
        self.failUnlessEqual(r.sig, 'sigblob')


    def test_checkAuthMissingSignature(self):
        args = {
            'openid.mode': 'check_authentication',
            'openid.assoc_handle': '{dumb}{handle}',
            'openid.signed': 'foo,bar,mode',
            'openid.foo': 'signedval1',
            'openid.bar': 'signedval2',
            'openid.baz': 'unsigned',
            }
        self.failUnlessRaises(server.ProtocolError, self.decode, args)


    def test_checkAuthAndInvalidate(self):
        args = {
            'openid.mode': 'check_authentication',
            'openid.assoc_handle': '{dumb}{handle}',
            'openid.invalidate_handle': '[[SMART_handle]]',
            'openid.sig': 'sigblob',
            'openid.signed': 'identity,return_to,response_nonce,mode',
            'openid.identity': 'signedval1',
            'openid.return_to': 'signedval2',
            'openid.response_nonce': 'signedval3',
            'openid.baz': 'unsigned',
            }
        r = self.decode(args)
        self.failUnless(isinstance(r, server.CheckAuthRequest))
        self.failUnlessEqual(r.invalidate_handle, '[[SMART_handle]]')


    def test_associateDH(self):
        args = {
            'openid.mode': 'associate',
            'openid.session_type': 'DH-SHA1',
            'openid.dh_consumer_public': "Rzup9265tw==",
            }
        r = self.decode(args)
        self.failUnless(isinstance(r, server.AssociateRequest))
        self.failUnlessEqual(r.mode, "associate")
        self.failUnlessEqual(r.session.session_type, "DH-SHA1")
        self.failUnlessEqual(r.assoc_type, "HMAC-SHA1")
        self.failUnless(r.session.consumer_pubkey)

    def test_associateDHMissingKey(self):
        """Trying DH assoc w/o public key"""
        args = {
            'openid.mode': 'associate',
            'openid.session_type': 'DH-SHA1',
            }
        # Using DH-SHA1 without supplying dh_consumer_public is an error.
        self.failUnlessRaises(server.ProtocolError, self.decode, args)


    def test_associateDHpubKeyNotB64(self):
        args = {
            'openid.mode': 'associate',
            'openid.session_type': 'DH-SHA1',
            'openid.dh_consumer_public': "donkeydonkeydonkey",
            }
        self.failUnlessRaises(server.ProtocolError, self.decode, args)


    def test_associateDHModGen(self):
        # test dh with non-default but valid values for dh_modulus and dh_gen
        args = {
            'openid.mode': 'associate',
            'openid.session_type': 'DH-SHA1',
            'openid.dh_consumer_public': "Rzup9265tw==",
            'openid.dh_modulus': cryptutil.longToBase64(ALT_MODULUS),
            'openid.dh_gen': cryptutil.longToBase64(ALT_GEN) ,
            }
        r = self.decode(args)
        self.failUnless(isinstance(r, server.AssociateRequest))
        self.failUnlessEqual(r.mode, "associate")
        self.failUnlessEqual(r.session.session_type, "DH-SHA1")
        self.failUnlessEqual(r.assoc_type, "HMAC-SHA1")
        self.failUnlessEqual(r.session.dh.modulus, ALT_MODULUS)
        self.failUnlessEqual(r.session.dh.generator, ALT_GEN)
        self.failUnless(r.session.consumer_pubkey)


    def test_associateDHCorruptModGen(self):
        # test dh with non-default but valid values for dh_modulus and dh_gen
        args = {
            'openid.mode': 'associate',
            'openid.session_type': 'DH-SHA1',
            'openid.dh_consumer_public': "Rzup9265tw==",
            'openid.dh_modulus': 'pizza',
            'openid.dh_gen': 'gnocchi',
            }
        self.failUnlessRaises(server.ProtocolError, self.decode, args)


    def test_associateDHMissingModGen(self):
        # test dh with non-default but valid values for dh_modulus and dh_gen
        args = {
            'openid.mode': 'associate',
            'openid.session_type': 'DH-SHA1',
            'openid.dh_consumer_public': "Rzup9265tw==",
            'openid.dh_modulus': 'pizza',
            }
        self.failUnlessRaises(server.ProtocolError, self.decode, args)


#     def test_associateDHInvalidModGen(self):
#         # test dh with properly encoded values that are not a valid
#         #   modulus/generator combination.
#         args = {
#             'openid.mode': 'associate',
#             'openid.session_type': 'DH-SHA1',
#             'openid.dh_consumer_public': "Rzup9265tw==",
#             'openid.dh_modulus': cryptutil.longToBase64(9),
#             'openid.dh_gen': cryptutil.longToBase64(27) ,
#             }
#         self.failUnlessRaises(server.ProtocolError, self.decode, args)
#     test_associateDHInvalidModGen.todo = "low-priority feature"


    def test_associateWeirdSession(self):
        args = {
            'openid.mode': 'associate',
            'openid.session_type': 'FLCL6',
            'openid.dh_consumer_public': "YQ==\n",
            }
        self.failUnlessRaises(server.ProtocolError, self.decode, args)


    def test_associatePlain(self):
        args = {
            'openid.mode': 'associate',
            }
        r = self.decode(args)
        self.failUnless(isinstance(r, server.AssociateRequest))
        self.failUnlessEqual(r.mode, "associate")
        self.failUnlessEqual(r.session.session_type, "no-encryption")
        self.failUnlessEqual(r.assoc_type, "HMAC-SHA1")

    def test_nomode(self):
        args = {
            'openid.session_type': 'DH-SHA1',
            'openid.dh_consumer_public': "my public keeey",
            }
        self.failUnlessRaises(server.ProtocolError, self.decode, args)



class TestEncode(unittest.TestCase):
    def setUp(self):
        self.encoder = server.Encoder()
        self.encode = self.encoder.encode
        self.op_endpoint = 'http://endpoint.unittest/encode'
        self.store = memstore.MemoryStore()
        self.server = server.Server(self.store, self.op_endpoint)

    def test_id_res_OpenID2_GET(self):
        """
        Check that when an OpenID 2 response does not exceed the
        OpenID 1 message size, a GET response (i.e., redirect) is
        issued.
        """
        request = server.CheckIDRequest(
            identity = 'http://bombom.unittest/',
            trust_root = 'http://burr.unittest/',
            return_to = 'http://burr.unittest/999',
            immediate = False,
            op_endpoint = self.server.op_endpoint,
            )
        response = server.OpenIDResponse(request)
        response.fields = Message.fromOpenIDArgs({
            'ns': OPENID2_NS,
            'mode': 'id_res',
            'identity': request.identity,
            'claimed_id': request.identity,
            'return_to': request.return_to,
            })

        self.failIf(response.renderAsForm())
        self.failUnless(response.whichEncoding() == server.ENCODE_URL)
        webresponse = self.encode(response)
        self.failUnless(webresponse.headers.has_key('location'))

    def test_id_res_OpenID2_POST(self):
        """
        Check that when an OpenID 2 response exceeds the OpenID 1
        message size, a POST response (i.e., an HTML form) is
        returned.
        """
        request = server.CheckIDRequest(
            identity = 'http://bombom.unittest/',
            trust_root = 'http://burr.unittest/',
            return_to = 'http://burr.unittest/999',
            immediate = False,
            op_endpoint = self.server.op_endpoint,
            )
        response = server.OpenIDResponse(request)
        response.fields = Message.fromOpenIDArgs({
            'ns': OPENID2_NS,
            'mode': 'id_res',
            'identity': request.identity,
            'claimed_id': request.identity,
            'return_to': 'x' * OPENID1_URL_LIMIT,
            })

        self.failUnless(response.renderAsForm())
        self.failUnless(len(response.encodeToURL()) > OPENID1_URL_LIMIT)
        self.failUnless(response.whichEncoding() == server.ENCODE_HTML_FORM)
        webresponse = self.encode(response)
        self.failUnlessEqual(webresponse.body, response.toFormMarkup())

    def test_id_res_OpenID1_exceeds_limit(self):
        """
        Check that when an OpenID 1 response exceeds the OpenID 1
        message size, a GET response is issued.  Technically, this
        shouldn't be permitted by the library, but this test is in
        place to preserve the status quo for OpenID 1.
        """
        request = server.CheckIDRequest(
            identity = 'http://bombom.unittest/',
            trust_root = 'http://burr.unittest/',
            return_to = 'http://burr.unittest/999',
            immediate = False,
            op_endpoint = self.server.op_endpoint,
            )
        response = server.OpenIDResponse(request)
        response.fields = Message.fromOpenIDArgs({
            'mode': 'id_res',
            'identity': request.identity,
            'return_to': 'x' * OPENID1_URL_LIMIT,
            })

        self.failIf(response.renderAsForm())
        self.failUnless(len(response.encodeToURL()) > OPENID1_URL_LIMIT)
        self.failUnless(response.whichEncoding() == server.ENCODE_URL)
        webresponse = self.encode(response)
        self.failUnlessEqual(webresponse.headers['location'], response.encodeToURL())

    def test_id_res(self):
        request = server.CheckIDRequest(
            identity = 'http://bombom.unittest/',
            trust_root = 'http://burr.unittest/',
            return_to = 'http://burr.unittest/999',
            immediate = False,
            op_endpoint = self.server.op_endpoint,
            )
        response = server.OpenIDResponse(request)
        response.fields = Message.fromOpenIDArgs({
            'mode': 'id_res',
            'identity': request.identity,
            'return_to': request.return_to,
            })
        webresponse = self.encode(response)
        self.failUnlessEqual(webresponse.code, server.HTTP_REDIRECT)
        self.failUnless(webresponse.headers.has_key('location'))

        location = webresponse.headers['location']
        self.failUnless(location.startswith(request.return_to),
                        "%s does not start with %s" % (location,
                                                       request.return_to))
        # argh.
        q2 = dict(cgi.parse_qsl(urlparse(location)[4]))
        expected = response.fields.toPostArgs()
        self.failUnlessEqual(q2, expected)

    def test_cancel(self):
        request = server.CheckIDRequest(
            identity = 'http://bombom.unittest/',
            trust_root = 'http://burr.unittest/',
            return_to = 'http://burr.unittest/999',
            immediate = False,
            op_endpoint = self.server.op_endpoint,
            )
        response = server.OpenIDResponse(request)
        response.fields = Message.fromOpenIDArgs({
            'mode': 'cancel',
            })
        webresponse = self.encode(response)
        self.failUnlessEqual(webresponse.code, server.HTTP_REDIRECT)
        self.failUnless(webresponse.headers.has_key('location'))

    def test_assocReply(self):
        msg = Message(OPENID2_NS)
        msg.setArg(OPENID2_NS, 'session_type', 'no-encryption')
        request = server.AssociateRequest.fromMessage(msg)
        response = server.OpenIDResponse(request)
        response.fields = Message.fromPostArgs(
            {'openid.assoc_handle': "every-zig"})
        webresponse = self.encode(response)
        body = """assoc_handle:every-zig
"""
        self.failUnlessEqual(webresponse.code, server.HTTP_OK)
        self.failUnlessEqual(webresponse.headers, {})
        self.failUnlessEqual(webresponse.body, body)

    def test_checkauthReply(self):
        request = server.CheckAuthRequest('a_sock_monkey',
                                          'siggggg',
                                          [])
        response = server.OpenIDResponse(request)
        response.fields = Message.fromOpenIDArgs({
            'is_valid': 'true',
            'invalidate_handle': 'xXxX:xXXx'
            })
        body = """invalidate_handle:xXxX:xXXx
is_valid:true
"""
        webresponse = self.encode(response)
        self.failUnlessEqual(webresponse.code, server.HTTP_OK)
        self.failUnlessEqual(webresponse.headers, {})
        self.failUnlessEqual(webresponse.body, body)

    def test_unencodableError(self):
        args = Message.fromPostArgs({
            'openid.identity': 'http://limu.unittest/',
            })
        e = server.ProtocolError(args, "wet paint")
        self.failUnlessRaises(server.EncodingError, self.encode, e)

    def test_encodableError(self):
        args = Message.fromPostArgs({
            'openid.mode': 'associate',
            'openid.identity': 'http://limu.unittest/',
            })
        body="error:snoot\nmode:error\n"
        webresponse = self.encode(server.ProtocolError(args, "snoot"))
        self.failUnlessEqual(webresponse.code, server.HTTP_ERROR)
        self.failUnlessEqual(webresponse.headers, {})
        self.failUnlessEqual(webresponse.body, body)



class TestSigningEncode(unittest.TestCase):
    def setUp(self):
        self._dumb_key = server.Signatory._dumb_key
        self._normal_key = server.Signatory._normal_key
        self.store = memstore.MemoryStore()
        self.server = server.Server(self.store, "http://signing.unittest/enc")
        self.request = server.CheckIDRequest(
            identity = 'http://bombom.unittest/',
            trust_root = 'http://burr.unittest/',
            return_to = 'http://burr.unittest/999',
            immediate = False,
            op_endpoint = self.server.op_endpoint,
            )
        self.response = server.OpenIDResponse(self.request)
        self.response.fields = Message.fromOpenIDArgs({
            'mode': 'id_res',
            'identity': self.request.identity,
            'return_to': self.request.return_to,
            })
        self.signatory = server.Signatory(self.store)
        self.encoder = server.SigningEncoder(self.signatory)
        self.encode = self.encoder.encode

    def test_idres(self):
        assoc_handle = '{bicycle}{shed}'
        self.store.storeAssociation(
            self._normal_key,
            association.Association.fromExpiresIn(60, assoc_handle,
                                                  'sekrit', 'HMAC-SHA1'))
        self.request.assoc_handle = assoc_handle
        webresponse = self.encode(self.response)
        self.failUnlessEqual(webresponse.code, server.HTTP_REDIRECT)
        self.failUnless(webresponse.headers.has_key('location'))

        location = webresponse.headers['location']
        query = cgi.parse_qs(urlparse(location)[4])
        self.failUnless('openid.sig' in query)
        self.failUnless('openid.assoc_handle' in query)
        self.failUnless('openid.signed' in query)

    def test_idresDumb(self):
        webresponse = self.encode(self.response)
        self.failUnlessEqual(webresponse.code, server.HTTP_REDIRECT)
        self.failUnless(webresponse.headers.has_key('location'))

        location = webresponse.headers['location']
        query = cgi.parse_qs(urlparse(location)[4])
        self.failUnless('openid.sig' in query)
        self.failUnless('openid.assoc_handle' in query)
        self.failUnless('openid.signed' in query)

    def test_forgotStore(self):
        self.encoder.signatory = None
        self.failUnlessRaises(ValueError, self.encode, self.response)

    def test_cancel(self):
        request = server.CheckIDRequest(
            identity = 'http://bombom.unittest/',
            trust_root = 'http://burr.unittest/',
            return_to = 'http://burr.unittest/999',
            immediate = False,
            op_endpoint = self.server.op_endpoint,
            )
        response = server.OpenIDResponse(request)
        response.fields.setArg(OPENID_NS, 'mode', 'cancel')
        webresponse = self.encode(response)
        self.failUnlessEqual(webresponse.code, server.HTTP_REDIRECT)
        self.failUnless(webresponse.headers.has_key('location'))
        location = webresponse.headers['location']
        query = cgi.parse_qs(urlparse(location)[4])
        self.failIf('openid.sig' in query, response.fields.toPostArgs())

    def test_assocReply(self):
        msg = Message(OPENID2_NS)
        msg.setArg(OPENID2_NS, 'session_type', 'no-encryption')
        request = server.AssociateRequest.fromMessage(msg)
        response = server.OpenIDResponse(request)
        response.fields = Message.fromOpenIDArgs({'assoc_handle': "every-zig"})
        webresponse = self.encode(response)
        body = """assoc_handle:every-zig
"""
        self.failUnlessEqual(webresponse.code, server.HTTP_OK)
        self.failUnlessEqual(webresponse.headers, {})
        self.failUnlessEqual(webresponse.body, body)

    def test_alreadySigned(self):
        self.response.fields.setArg(OPENID_NS, 'sig', 'priorSig==')
        self.failUnlessRaises(server.AlreadySigned, self.encode, self.response)

class TestCheckID(unittest.TestCase):
    def setUp(self):
        self.op_endpoint = 'http://endpoint.unittest/'
        self.store = memstore.MemoryStore()
        self.server = server.Server(self.store, self.op_endpoint)
        self.request = server.CheckIDRequest(
            identity = 'http://bambam.unittest/',
            trust_root = 'http://bar.unittest/',
            return_to = 'http://bar.unittest/999',
            immediate = False,
            op_endpoint = self.server.op_endpoint,
            )

    def test_trustRootInvalid(self):
        self.request.trust_root = "http://foo.unittest/17"
        self.request.return_to = "http://foo.unittest/39"
        self.failIf(self.request.trustRootValid())

    def test_trustRootValid(self):
        self.request.trust_root = "http://foo.unittest/"
        self.request.return_to = "http://foo.unittest/39"
        self.failUnless(self.request.trustRootValid())

    def test_trustRootValidNoReturnTo(self):
        request = server.CheckIDRequest(
            identity = 'http://bambam.unittest/',
            trust_root = 'http://bar.unittest/',
            return_to = None,
            immediate = False,
            op_endpoint = self.server.op_endpoint,
            )

        self.failUnless(request.trustRootValid())

    def test_returnToVerified_callsVerify(self):
        """Make sure that verifyReturnTo is calling the trustroot
        function verifyReturnTo
        """
        def withVerifyReturnTo(new_verify, callable):
            old_verify = server.verifyReturnTo
            try:
                server.verifyReturnTo = new_verify
                return callable()
            finally:
                server.verifyReturnTo = old_verify

        # Ensure that exceptions are passed through
        sentinel = Exception()
        def vrfyExc(trust_root, return_to):
            self.failUnlessEqual(self.request.trust_root, trust_root)
            self.failUnlessEqual(self.request.return_to, return_to)
            raise sentinel

        try:
            withVerifyReturnTo(vrfyExc, self.request.returnToVerified)
        except Exception, e:
            self.failUnless(e is sentinel, e)

        # Ensure that True and False are passed through unchanged
        def constVerify(val):
            def verify(trust_root, return_to):
                self.failUnlessEqual(self.request.trust_root, trust_root)
                self.failUnlessEqual(self.request.return_to, return_to)
                return val
            return verify

        for val in [True, False]:
            self.failUnlessEqual(
                val,
                withVerifyReturnTo(constVerify(val),
                                   self.request.returnToVerified))

    def _expectAnswer(self, answer, identity=None, claimed_id=None):
        expected_list = [
            ('mode', 'id_res'),
            ('return_to', self.request.return_to),
            ('op_endpoint', self.op_endpoint),
            ]
        if identity:
            expected_list.append(('identity', identity))
            if claimed_id:
                expected_list.append(('claimed_id', claimed_id))
            else:
                expected_list.append(('claimed_id', identity))

        for k, expected in expected_list:
            actual = answer.fields.getArg(OPENID_NS, k)
            self.failUnlessEqual(actual, expected, "%s: expected %s, got %s" % (k, expected, actual))

        self.failUnless(answer.fields.hasKey(OPENID_NS, 'response_nonce'))
        self.failUnless(answer.fields.getOpenIDNamespace() == OPENID2_NS)

        # One for nonce, one for ns
        self.failUnlessEqual(len(answer.fields.toPostArgs()),
                             len(expected_list) + 2,
                             answer.fields.toPostArgs())

    def _expectAnswerv1(self, answer, identity=None):
        expected_list = [
            ('mode', 'id_res'),
            ('return_to', self.request.return_to),
            ('identity', identity),
            ]

        for k, expected in expected_list:
            actual = answer.fields.getArg(OPENID_NS, k)
            self.failUnlessEqual(actual, expected, "%s: expected %s, got %s" % (k, expected, actual))

        self.failUnless(answer.fields.hasKey(OPENID_NS, 'response_nonce'))
        self.failUnlessEqual(answer.fields.getOpenIDNamespace(), OPENID1_NS)

        # One for nonce
        self.failUnlessEqual(len(answer.fields.toPostArgs()),
                             len(expected_list) + 1,
                             answer.fields.toPostArgs())


    def test_answerAllow(self):
        """Check the fields specified by "Positive Assertions"

        including mode=id_res, identity, claimed_id, op_endpoint, return_to
        """
        answer = self.request.answer(True)
        self.failUnlessEqual(answer.request, self.request)
        self._expectAnswer(answer, self.request.identity)

    def test_answerAllowDelegatedIdentity(self):
        self.request.claimed_id = 'http://delegating.unittest/'
        answer = self.request.answer(True)
        self._expectAnswer(answer, self.request.identity,
                           self.request.claimed_id)

    def test_answerAllowWithoutIdentityReally(self):
        self.request.identity = None
        answer = self.request.answer(True)
        self.failUnlessEqual(answer.request, self.request)
        self._expectAnswer(answer)

    def test_answerAllowAnonymousFail(self):
        self.request.identity = None
        # XXX - Check on this, I think this behavior is legal in OpenID 2.0?
        self.failUnlessRaises(
            ValueError, self.request.answer, True, identity="=V")

    def test_answerAllowWithIdentity(self):
        self.request.identity = IDENTIFIER_SELECT
        selected_id = 'http://anon.unittest/9861'
        answer = self.request.answer(True, identity=selected_id)
        self._expectAnswer(answer, selected_id)

    def test_answerAllowWithDelegatedIdentityOpenID2(self):
        """Answer an IDENTIFIER_SELECT case with a delegated identifier.
        """
        # claimed_id delegates to selected_id here.
        self.request.identity = IDENTIFIER_SELECT
        selected_id = 'http://anon.unittest/9861'
        claimed_id = 'http://monkeyhat.unittest/'
        answer = self.request.answer(True, identity=selected_id,
                                     claimed_id=claimed_id)
        self._expectAnswer(answer, selected_id, claimed_id)

    def test_answerAllowWithDelegatedIdentityOpenID1(self):
        """claimed_id parameter doesn't exist in OpenID 1.
        """
        self.request.namespace = OPENID1_NS
        # claimed_id delegates to selected_id here.
        self.request.identity = IDENTIFIER_SELECT
        selected_id = 'http://anon.unittest/9861'
        claimed_id = 'http://monkeyhat.unittest/'
        self.failUnlessRaises(server.VersionError,
                              self.request.answer, True,
                              identity=selected_id,
                              claimed_id=claimed_id)

    def test_answerAllowWithAnotherIdentity(self):
        # XXX - Check on this, I think this behavior is legal in OpenID 2.0?
        self.failUnlessRaises(ValueError, self.request.answer, True,
                              identity="http://pebbles.unittest/")

    def test_answerAllowNoIdentityOpenID1(self):
        self.request.namespace = OPENID1_NS
        self.request.identity = None
        self.failUnlessRaises(ValueError, self.request.answer, True,
                              identity=None)

    def test_answerAllowForgotEndpoint(self):
        self.request.op_endpoint = None
        self.failUnlessRaises(RuntimeError, self.request.answer, True)

    def test_checkIDWithNoIdentityOpenID1(self):
        msg = Message(OPENID1_NS)
        msg.setArg(OPENID_NS, 'return_to', 'bogus')
        msg.setArg(OPENID_NS, 'trust_root', 'bogus')
        msg.setArg(OPENID_NS, 'mode', 'checkid_setup')
        msg.setArg(OPENID_NS, 'assoc_handle', 'bogus')

        self.failUnlessRaises(server.ProtocolError,
                              server.CheckIDRequest.fromMessage,
                              msg, self.server)

    def test_trustRootOpenID1(self):
        """Ignore openid.realm in OpenID 1"""
        msg = Message(OPENID1_NS)
        msg.setArg(OPENID_NS, 'mode', 'checkid_setup')
        msg.setArg(OPENID_NS, 'trust_root', 'http://real_trust_root/')
        msg.setArg(OPENID_NS, 'realm', 'http://fake_trust_root/')
        msg.setArg(OPENID_NS, 'return_to', 'http://real_trust_root/foo')
        msg.setArg(OPENID_NS, 'assoc_handle', 'bogus')
        msg.setArg(OPENID_NS, 'identity', 'george')

        result = server.CheckIDRequest.fromMessage(msg, self.server.op_endpoint)

        self.failUnless(result.trust_root == 'http://real_trust_root/')

    def test_trustRootOpenID2(self):
        """Ignore openid.trust_root in OpenID 2"""
        msg = Message(OPENID2_NS)
        msg.setArg(OPENID_NS, 'mode', 'checkid_setup')
        msg.setArg(OPENID_NS, 'realm', 'http://real_trust_root/')
        msg.setArg(OPENID_NS, 'trust_root', 'http://fake_trust_root/')
        msg.setArg(OPENID_NS, 'return_to', 'http://real_trust_root/foo')
        msg.setArg(OPENID_NS, 'assoc_handle', 'bogus')
        msg.setArg(OPENID_NS, 'identity', 'george')
        msg.setArg(OPENID_NS, 'claimed_id', 'george')

        result = server.CheckIDRequest.fromMessage(msg, self.server.op_endpoint)

        self.failUnless(result.trust_root == 'http://real_trust_root/')

    def test_answerAllowNoTrustRoot(self):
        self.request.trust_root = None
        answer = self.request.answer(True)
        self.failUnlessEqual(answer.request, self.request)
        self._expectAnswer(answer, self.request.identity)

    def test_answerAllowNoEndpointOpenID1(self):
        """Test .allow() with an OpenID 1.x Message on a CheckIDRequest
        built without an op_endpoint parameter.
        """
        reqmessage = Message.fromOpenIDArgs({
            'identity': 'http://bambam.unittest/',
            'trust_root': 'http://bar.unittest/',
            'return_to': 'http://bar.unittest/999',
            })
        self.request = server.CheckIDRequest.fromMessage(reqmessage, None)
        answer = self.request.answer(True)
        self._expectAnswerv1(answer, 'http://bambam.unittest/')

    def test_answerImmediateDenyOpenID2(self):
        """Look for mode=setup_needed in checkid_immediate negative
        response in OpenID 2 case.

        See specification Responding to Authentication Requests /
        Negative Assertions / In Response to Immediate Requests.
        """
        self.request.mode = 'checkid_immediate'
        self.request.immediate = True
        server_url = "http://setup-url.unittest/"
        # crappiting setup_url, you dirty my interface with your presence!
        answer = self.request.answer(False, server_url=server_url)
        self.failUnlessEqual(answer.request, self.request)
        self.failUnlessEqual(len(answer.fields.toPostArgs()), 3, answer.fields)
        self.failUnlessEqual(answer.fields.getOpenIDNamespace(), OPENID2_NS)
        self.failUnlessEqual(answer.fields.getArg(OPENID_NS, 'mode'),
                             'setup_needed')
        # user_setup_url no longer required.

    def test_answerImmediateDenyOpenID1(self):
        """Look for user_setup_url in checkid_immediate negative
        response in OpenID 1 case."""
        self.request.namespace = OPENID1_NS
        self.request.mode = 'checkid_immediate'
        self.request.immediate = True
        server_url = "http://setup-url.unittest/"
        # crappiting setup_url, you dirty my interface with your presence!
        answer = self.request.answer(False, server_url=server_url)
        self.failUnlessEqual(answer.request, self.request)
        self.failUnlessEqual(len(answer.fields.toPostArgs()), 2, answer.fields)
        self.failUnlessEqual(answer.fields.getOpenIDNamespace(), OPENID1_NS)
        self.failUnlessEqual(answer.fields.getArg(OPENID_NS, 'mode'), 'id_res')
        self.failUnless(answer.fields.getArg(
            OPENID_NS, 'user_setup_url', '').startswith(server_url))

    def test_answerSetupDeny(self):
        answer = self.request.answer(False)
        self.failUnlessEqual(answer.fields.getArgs(OPENID_NS), {
            'mode': 'cancel',
            })

    def test_encodeToURL(self):
        server_url = 'http://openid-server.unittest/'
        result = self.request.encodeToURL(server_url)

        # How to check?  How about a round-trip test.
        base, result_args = result.split('?', 1)
        result_args = dict(cgi.parse_qsl(result_args))
        message = Message.fromPostArgs(result_args)
        rebuilt_request = server.CheckIDRequest.fromMessage(message,
                                                            self.server.op_endpoint)
        # argh, lousy hack
        self.request.message = message
        self.failUnlessEqual(rebuilt_request.__dict__, self.request.__dict__)

    def test_getCancelURL(self):
        url = self.request.getCancelURL()
        rt, query_string = url.split('?')
        self.failUnlessEqual(self.request.return_to, rt)
        query = dict(cgi.parse_qsl(query_string))
        self.failUnlessEqual(query, {'openid.mode':'cancel',
                                     'openid.ns':OPENID2_NS})

    def test_getCancelURLimmed(self):
        self.request.mode = 'checkid_immediate'
        self.request.immediate = True
        self.failUnlessRaises(ValueError, self.request.getCancelURL)



class TestCheckIDExtension(unittest.TestCase):

    def setUp(self):
        self.op_endpoint = 'http://endpoint.unittest/ext'
        self.store = memstore.MemoryStore()
        self.server = server.Server(self.store, self.op_endpoint)
        self.request = server.CheckIDRequest(
            identity = 'http://bambam.unittest/',
            trust_root = 'http://bar.unittest/',
            return_to = 'http://bar.unittest/999',
            immediate = False,
            op_endpoint = self.server.op_endpoint,
            )
        self.response = server.OpenIDResponse(self.request)
        self.response.fields.setArg(OPENID_NS, 'mode', 'id_res')
        self.response.fields.setArg(OPENID_NS, 'blue', 'star')


    def test_addField(self):
        namespace = 'something:'
        self.response.fields.setArg(namespace, 'bright', 'potato')
        self.failUnlessEqual(self.response.fields.getArgs(OPENID_NS),
                             {'blue': 'star',
                              'mode': 'id_res',
                              })
        
        self.failUnlessEqual(self.response.fields.getArgs(namespace),
                             {'bright':'potato'})


    def test_addFields(self):
        namespace = 'mi5:'
        args =  {'tangy': 'suspenders',
                 'bravo': 'inclusion'}
        self.response.fields.updateArgs(namespace, args)
        self.failUnlessEqual(self.response.fields.getArgs(OPENID_NS),
                             {'blue': 'star',
                              'mode': 'id_res',
                              })
        self.failUnlessEqual(self.response.fields.getArgs(namespace), args)



class MockSignatory(object):
    isValid = True

    def __init__(self, assoc):
        self.assocs = [assoc]

    def verify(self, assoc_handle, message):
        assert message.hasKey(OPENID_NS, "sig")
        if (True, assoc_handle) in self.assocs:
            return self.isValid
        else:
            return False

    def getAssociation(self, assoc_handle, dumb):
        if (dumb, assoc_handle) in self.assocs:
            # This isn't a valid implementation for many uses of this
            # function, mind you.
            return True
        else:
            return None

    def invalidate(self, assoc_handle, dumb):
        if (dumb, assoc_handle) in self.assocs:
            self.assocs.remove((dumb, assoc_handle))


class TestCheckAuth(unittest.TestCase):
    def setUp(self):
        self.assoc_handle = 'mooooooooo'
        self.message = Message.fromPostArgs({
            'openid.sig': 'signarture',
            'one': 'alpha',
            'two': 'beta',
            })
        self.request = server.CheckAuthRequest(
            self.assoc_handle, self.message)

        self.signatory = MockSignatory((True, self.assoc_handle))

    def test_valid(self):
        r = self.request.answer(self.signatory)
        self.failUnlessEqual(r.fields.getArgs(OPENID_NS), {'is_valid': 'true'})
        self.failUnlessEqual(r.request, self.request)

    def test_invalid(self):
        self.signatory.isValid = False
        r = self.request.answer(self.signatory)
        self.failUnlessEqual(r.fields.getArgs(OPENID_NS),
                             {'is_valid': 'false'})

    def test_replay(self):
        """Don't validate the same response twice.

        From "Checking the Nonce"::
        
            When using "check_authentication", the OP MUST ensure that an
            assertion has not yet been accepted with the same value for
            "openid.response_nonce".

        In this implementation, the assoc_handle is only valid once.  And
        nonces are a signed component of the message, so they can't be used
        with another handle without breaking the sig.
        """
        r = self.request.answer(self.signatory)
        r = self.request.answer(self.signatory)
        self.failUnlessEqual(r.fields.getArgs(OPENID_NS),
                             {'is_valid': 'false'})

    def test_invalidatehandle(self):
        self.request.invalidate_handle = "bogusHandle"
        r = self.request.answer(self.signatory)
        self.failUnlessEqual(r.fields.getArgs(OPENID_NS),
                             {'is_valid': 'true',
                              'invalidate_handle': "bogusHandle"})
        self.failUnlessEqual(r.request, self.request)

    def test_invalidatehandleNo(self):
        assoc_handle = 'goodhandle'
        self.signatory.assocs.append((False, 'goodhandle'))
        self.request.invalidate_handle = assoc_handle
        r = self.request.answer(self.signatory)
        self.failUnlessEqual(r.fields.getArgs(OPENID_NS), {'is_valid': 'true'})


class TestAssociate(unittest.TestCase):
    # TODO: test DH with non-default values for modulus and gen.
    # (important to do because we actually had it broken for a while.)

    def setUp(self):
        self.request = server.AssociateRequest.fromMessage(
            Message.fromPostArgs({}))
        self.store = memstore.MemoryStore()
        self.signatory = server.Signatory(self.store)

    def test_dhSHA1(self):
        self.assoc = self.signatory.createAssociation(dumb=False, assoc_type='HMAC-SHA1')
        from openid.dh import DiffieHellman
        from openid.server.server import DiffieHellmanSHA1ServerSession
        consumer_dh = DiffieHellman.fromDefaults()
        cpub = consumer_dh.public
        server_dh = DiffieHellman.fromDefaults()
        session = DiffieHellmanSHA1ServerSession(server_dh, cpub)
        self.request = server.AssociateRequest(session, 'HMAC-SHA1')
        response = self.request.answer(self.assoc)
        rfg = lambda f: response.fields.getArg(OPENID_NS, f)
        self.failUnlessEqual(rfg("assoc_type"), "HMAC-SHA1")
        self.failUnlessEqual(rfg("assoc_handle"), self.assoc.handle)
        self.failIf(rfg("mac_key"))
        self.failUnlessEqual(rfg("session_type"), "DH-SHA1")
        self.failUnless(rfg("enc_mac_key"))
        self.failUnless(rfg("dh_server_public"))

        enc_key = rfg("enc_mac_key").decode('base64')
        spub = cryptutil.base64ToLong(rfg("dh_server_public"))
        secret = consumer_dh.xorSecret(spub, enc_key, cryptutil.sha1)
        self.failUnlessEqual(secret, self.assoc.secret)


    if not cryptutil.SHA256_AVAILABLE:
        warnings.warn("Not running SHA256 tests.")
    else:
        def test_dhSHA256(self):
            self.assoc = self.signatory.createAssociation(
                dumb=False, assoc_type='HMAC-SHA256')
            from openid.dh import DiffieHellman
            from openid.server.server import DiffieHellmanSHA256ServerSession
            consumer_dh = DiffieHellman.fromDefaults()
            cpub = consumer_dh.public
            server_dh = DiffieHellman.fromDefaults()
            session = DiffieHellmanSHA256ServerSession(server_dh, cpub)
            self.request = server.AssociateRequest(session, 'HMAC-SHA256')
            response = self.request.answer(self.assoc)
            rfg = lambda f: response.fields.getArg(OPENID_NS, f)
            self.failUnlessEqual(rfg("assoc_type"), "HMAC-SHA256")
            self.failUnlessEqual(rfg("assoc_handle"), self.assoc.handle)
            self.failIf(rfg("mac_key"))
            self.failUnlessEqual(rfg("session_type"), "DH-SHA256")
            self.failUnless(rfg("enc_mac_key"))
            self.failUnless(rfg("dh_server_public"))

            enc_key = rfg("enc_mac_key").decode('base64')
            spub = cryptutil.base64ToLong(rfg("dh_server_public"))
            secret = consumer_dh.xorSecret(spub, enc_key, cryptutil.sha256)
            self.failUnlessEqual(secret, self.assoc.secret)

        def test_protoError256(self):
            from openid.consumer.consumer import \
                 DiffieHellmanSHA256ConsumerSession

            s256_session = DiffieHellmanSHA256ConsumerSession()

            invalid_s256 = {'openid.assoc_type':'HMAC-SHA1',
                            'openid.session_type':'DH-SHA256',}
            invalid_s256.update(s256_session.getRequest())

            invalid_s256_2 = {'openid.assoc_type':'MONKEY-PIRATE',
                              'openid.session_type':'DH-SHA256',}
            invalid_s256_2.update(s256_session.getRequest())

            bad_request_argss = [
                invalid_s256,
                invalid_s256_2,
                ]

            for request_args in bad_request_argss:
                message = Message.fromPostArgs(request_args)
                self.failUnlessRaises(server.ProtocolError,
                                      server.AssociateRequest.fromMessage,
                                      message)

    def test_protoError(self):
        from openid.consumer.consumer import DiffieHellmanSHA1ConsumerSession
            
        s1_session = DiffieHellmanSHA1ConsumerSession()

        invalid_s1 = {'openid.assoc_type':'HMAC-SHA256',
                      'openid.session_type':'DH-SHA1',}
        invalid_s1.update(s1_session.getRequest())

        invalid_s1_2 = {'openid.assoc_type':'ROBOT-NINJA',
                      'openid.session_type':'DH-SHA1',}
        invalid_s1_2.update(s1_session.getRequest())

        bad_request_argss = [
            {'openid.assoc_type':'Wha?'},
            invalid_s1,
            invalid_s1_2,
            ]
            
        for request_args in bad_request_argss:
            message = Message.fromPostArgs(request_args)
            self.failUnlessRaises(server.ProtocolError,
                                  server.AssociateRequest.fromMessage,
                                  message)

    def test_protoErrorFields(self):

        contact = 'user@example.invalid'
        reference = 'Trac ticket number MAX_INT'
        error = 'poltergeist'

        openid1_args = {
            'openid.identitiy': 'invalid',
            'openid.mode': 'checkid_setup',
            }

        openid2_args = dict(openid1_args)
        openid2_args.update({'openid.ns': OPENID2_NS})

        # Check presence of optional fields in both protocol versions

        openid1_msg = Message.fromPostArgs(openid1_args)
        p = server.ProtocolError(openid1_msg, error,
                                 contact=contact, reference=reference)
        reply = p.toMessage()

        self.failUnlessEqual(reply.getArg(OPENID_NS, 'reference'), reference)
        self.failUnlessEqual(reply.getArg(OPENID_NS, 'contact'), contact)

        openid2_msg = Message.fromPostArgs(openid2_args)
        p = server.ProtocolError(openid2_msg, error,
                                 contact=contact, reference=reference)
        reply = p.toMessage()

        self.failUnlessEqual(reply.getArg(OPENID_NS, 'reference'), reference)
        self.failUnlessEqual(reply.getArg(OPENID_NS, 'contact'), contact)

    def failUnlessExpiresInMatches(self, msg, expected_expires_in):
        expires_in_str = msg.getArg(OPENID_NS, 'expires_in', no_default)
        expires_in = int(expires_in_str)

        # Slop is necessary because the tests can sometimes get run
        # right on a second boundary
        slop = 1 # second
        difference = expected_expires_in - expires_in

        error_message = ('"expires_in" value not within %s of expected: '
                         'expected=%s, actual=%s' %
                         (slop, expected_expires_in, expires_in))
        self.failUnless(0 <= difference <= slop, error_message)

    def test_plaintext(self):
        self.assoc = self.signatory.createAssociation(dumb=False, assoc_type='HMAC-SHA1')
        response = self.request.answer(self.assoc)
        rfg = lambda f: response.fields.getArg(OPENID_NS, f)

        self.failUnlessEqual(rfg("assoc_type"), "HMAC-SHA1")
        self.failUnlessEqual(rfg("assoc_handle"), self.assoc.handle)

        self.failUnlessExpiresInMatches(
            response.fields, self.signatory.SECRET_LIFETIME)

        self.failUnlessEqual(
            rfg("mac_key"), oidutil.toBase64(self.assoc.secret))
        self.failIf(rfg("session_type"))
        self.failIf(rfg("enc_mac_key"))
        self.failIf(rfg("dh_server_public"))

    def test_plaintext256(self):
        self.assoc = self.signatory.createAssociation(dumb=False, assoc_type='HMAC-SHA256')
        response = self.request.answer(self.assoc)
        rfg = lambda f: response.fields.getArg(OPENID_NS, f)

        self.failUnlessEqual(rfg("assoc_type"), "HMAC-SHA1")
        self.failUnlessEqual(rfg("assoc_handle"), self.assoc.handle)

        self.failUnlessExpiresInMatches(
            response.fields, self.signatory.SECRET_LIFETIME)

        self.failUnlessEqual(
            rfg("mac_key"), oidutil.toBase64(self.assoc.secret))
        self.failIf(rfg("session_type"))
        self.failIf(rfg("enc_mac_key"))
        self.failIf(rfg("dh_server_public"))

    def test_unsupportedPrefer(self):
        allowed_assoc = 'COLD-PET-RAT'
        allowed_sess = 'FROG-BONES'
        message = 'This is a unit test'

        # Set an OpenID 2 message so answerUnsupported doesn't raise
        # ProtocolError.
        self.request.message = Message(OPENID2_NS)

        response = self.request.answerUnsupported(
            message=message,
            preferred_session_type=allowed_sess,
            preferred_association_type=allowed_assoc,
            )
        rfg = lambda f: response.fields.getArg(OPENID_NS, f)
        self.failUnlessEqual(rfg('error_code'), 'unsupported-type')
        self.failUnlessEqual(rfg('assoc_type'), allowed_assoc)
        self.failUnlessEqual(rfg('error'), message)
        self.failUnlessEqual(rfg('session_type'), allowed_sess)

    def test_unsupported(self):
        message = 'This is a unit test'

        # Set an OpenID 2 message so answerUnsupported doesn't raise
        # ProtocolError.
        self.request.message = Message(OPENID2_NS)

        response = self.request.answerUnsupported(message)
        rfg = lambda f: response.fields.getArg(OPENID_NS, f)
        self.failUnlessEqual(rfg('error_code'), 'unsupported-type')
        self.failUnlessEqual(rfg('assoc_type'), None)
        self.failUnlessEqual(rfg('error'), message)
        self.failUnlessEqual(rfg('session_type'), None)

class Counter(object):
    def __init__(self):
        self.count = 0

    def inc(self):
        self.count += 1

class TestServer(unittest.TestCase, CatchLogs):
    def setUp(self):
        self.store = memstore.MemoryStore()
        self.server = server.Server(self.store, "http://server.unittest/endpt")
        CatchLogs.setUp(self)

    def test_dispatch(self):
        monkeycalled = Counter()
        def monkeyDo(request):
            monkeycalled.inc()
            r = server.OpenIDResponse(request)
            return r
        self.server.openid_monkeymode = monkeyDo
        request = server.OpenIDRequest()
        request.mode = "monkeymode"
        request.namespace = OPENID1_NS
        webresult = self.server.handleRequest(request)
        self.failUnlessEqual(monkeycalled.count, 1)

    def test_associate(self):
        request = server.AssociateRequest.fromMessage(Message.fromPostArgs({}))
        response = self.server.openid_associate(request)
        self.failUnless(response.fields.hasKey(OPENID_NS, "assoc_handle"),
                        "No assoc_handle here: %s" % (response.fields,))

    def test_associate2(self):
        """Associate when the server has no allowed association types

        Gives back an error with error_code and no fallback session or
        assoc types."""
        self.server.negotiator.setAllowedTypes([])

        # Set an OpenID 2 message so answerUnsupported doesn't raise
        # ProtocolError.
        msg = Message.fromPostArgs({
            'openid.ns': OPENID2_NS,
            'openid.session_type': 'no-encryption',
            })

        request = server.AssociateRequest.fromMessage(msg)

        response = self.server.openid_associate(request)
        self.failUnless(response.fields.hasKey(OPENID_NS, "error"))
        self.failUnless(response.fields.hasKey(OPENID_NS, "error_code"))
        self.failIf(response.fields.hasKey(OPENID_NS, "assoc_handle"))
        self.failIf(response.fields.hasKey(OPENID_NS, "assoc_type"))
        self.failIf(response.fields.hasKey(OPENID_NS, "session_type"))

    def test_associate3(self):
        """Request an assoc type that is not supported when there are
        supported types.

        Should give back an error message with a fallback type.
        """
        self.server.negotiator.setAllowedTypes([('HMAC-SHA256', 'DH-SHA256')])

        msg = Message.fromPostArgs({
            'openid.ns': OPENID2_NS,
            'openid.session_type': 'no-encryption',
            })

        request = server.AssociateRequest.fromMessage(msg)
        response = self.server.openid_associate(request)

        self.failUnless(response.fields.hasKey(OPENID_NS, "error"))
        self.failUnless(response.fields.hasKey(OPENID_NS, "error_code"))
        self.failIf(response.fields.hasKey(OPENID_NS, "assoc_handle"))
        self.failUnlessEqual(response.fields.getArg(OPENID_NS, "assoc_type"),
                             'HMAC-SHA256')
        self.failUnlessEqual(response.fields.getArg(OPENID_NS, "session_type"),
                             'DH-SHA256')

    if not cryptutil.SHA256_AVAILABLE:
        warnings.warn("Not running SHA256 tests.")
    else:
        def test_associate4(self):
            """DH-SHA256 association session"""
            self.server.negotiator.setAllowedTypes(
                [('HMAC-SHA256', 'DH-SHA256')])
            query = {
                'openid.dh_consumer_public':
                'ALZgnx8N5Lgd7pCj8K86T/DDMFjJXSss1SKoLmxE72kJTzOtG6I2PaYrHX'
                'xku4jMQWSsGfLJxwCZ6280uYjUST/9NWmuAfcrBfmDHIBc3H8xh6RBnlXJ'
                '1WxJY3jHd5k1/ZReyRZOxZTKdF/dnIqwF8ZXUwI6peV0TyS/K1fOfF/s',
                'openid.assoc_type': 'HMAC-SHA256',
                'openid.session_type': 'DH-SHA256',
                }
            message = Message.fromPostArgs(query)
            request = server.AssociateRequest.fromMessage(message)
            response = self.server.openid_associate(request)
            self.failUnless(response.fields.hasKey(OPENID_NS, "assoc_handle"))

    def test_missingSessionTypeOpenID2(self):
        """Make sure session_type is required in OpenID 2"""
        msg = Message.fromPostArgs({
            'openid.ns': OPENID2_NS,
            })

        self.assertRaises(server.ProtocolError,
                          server.AssociateRequest.fromMessage, msg)

    def test_checkAuth(self):
        request = server.CheckAuthRequest('arrrrrf', '0x3999', [])
        response = self.server.openid_check_authentication(request)
        self.failUnless(response.fields.hasKey(OPENID_NS, "is_valid"))

class TestSignatory(unittest.TestCase, CatchLogs):
    def setUp(self):
        self.store = memstore.MemoryStore()
        self.signatory = server.Signatory(self.store)
        self._dumb_key = self.signatory._dumb_key
        self._normal_key = self.signatory._normal_key
        CatchLogs.setUp(self)

    def test_sign(self):
        request = server.OpenIDRequest()
        assoc_handle = '{assoc}{lookatme}'
        self.store.storeAssociation(
            self._normal_key,
            association.Association.fromExpiresIn(60, assoc_handle,
                                                  'sekrit', 'HMAC-SHA1'))
        request.assoc_handle = assoc_handle
        request.namespace = OPENID1_NS
        response = server.OpenIDResponse(request)
        response.fields = Message.fromOpenIDArgs({
            'foo': 'amsigned',
            'bar': 'notsigned',
            'azu': 'alsosigned',
            })
        sresponse = self.signatory.sign(response)
        self.failUnlessEqual(
            sresponse.fields.getArg(OPENID_NS, 'assoc_handle'),
            assoc_handle)
        self.failUnlessEqual(sresponse.fields.getArg(OPENID_NS, 'signed'),
                             'assoc_handle,azu,bar,foo,signed')
        self.failUnless(sresponse.fields.getArg(OPENID_NS, 'sig'))
        self.failIf(self.messages, self.messages)

    def test_signDumb(self):
        request = server.OpenIDRequest()
        request.assoc_handle = None
        request.namespace = OPENID2_NS
        response = server.OpenIDResponse(request)
        response.fields = Message.fromOpenIDArgs({
            'foo': 'amsigned',
            'bar': 'notsigned',
            'azu': 'alsosigned',
            'ns':OPENID2_NS,
            })
        sresponse = self.signatory.sign(response)
        assoc_handle = sresponse.fields.getArg(OPENID_NS, 'assoc_handle')
        self.failUnless(assoc_handle)
        assoc = self.signatory.getAssociation(assoc_handle, dumb=True)
        self.failUnless(assoc)
        self.failUnlessEqual(sresponse.fields.getArg(OPENID_NS, 'signed'),
                             'assoc_handle,azu,bar,foo,ns,signed')
        self.failUnless(sresponse.fields.getArg(OPENID_NS, 'sig'))
        self.failIf(self.messages, self.messages)

    def test_signExpired(self):
        """Sign a response to a message with an expired handle (using invalidate_handle).

        From "Verifying with an Association"::

            If an authentication request included an association handle for an
            association between the OP and the Relying party, and the OP no
            longer wishes to use that handle (because it has expired or the
            secret has been compromised, for instance), the OP will send a
            response that must be verified directly with the OP, as specified
            in Section 11.3.2. In that instance, the OP will include the field
            "openid.invalidate_handle" set to the association handle that the
            Relying Party included with the original request.
        """
        request = server.OpenIDRequest()
        request.namespace = OPENID2_NS
        assoc_handle = '{assoc}{lookatme}'
        self.store.storeAssociation(
            self._normal_key,
            association.Association.fromExpiresIn(-10, assoc_handle,
                                                  'sekrit', 'HMAC-SHA1'))
        self.failUnless(self.store.getAssociation(self._normal_key, assoc_handle))

        request.assoc_handle = assoc_handle
        response = server.OpenIDResponse(request)
        response.fields = Message.fromOpenIDArgs({
            'foo': 'amsigned',
            'bar': 'notsigned',
            'azu': 'alsosigned',
            })
        sresponse = self.signatory.sign(response)

        new_assoc_handle = sresponse.fields.getArg(OPENID_NS, 'assoc_handle')
        self.failUnless(new_assoc_handle)
        self.failIfEqual(new_assoc_handle, assoc_handle)

        self.failUnlessEqual(
            sresponse.fields.getArg(OPENID_NS, 'invalidate_handle'),
            assoc_handle)

        self.failUnlessEqual(sresponse.fields.getArg(OPENID_NS, 'signed'),
                             'assoc_handle,azu,bar,foo,invalidate_handle,signed')
        self.failUnless(sresponse.fields.getArg(OPENID_NS, 'sig'))

        # make sure the expired association is gone
        self.failIf(self.store.getAssociation(self._normal_key, assoc_handle),
                    "expired association is still retrievable.")

        # make sure the new key is a dumb mode association
        self.failUnless(self.store.getAssociation(self._dumb_key, new_assoc_handle))
        self.failIf(self.store.getAssociation(self._normal_key, new_assoc_handle))
        self.failUnless(self.messages)


    def test_signInvalidHandle(self):
        request = server.OpenIDRequest()
        request.namespace = OPENID2_NS
        assoc_handle = '{bogus-assoc}{notvalid}'

        request.assoc_handle = assoc_handle
        response = server.OpenIDResponse(request)
        response.fields = Message.fromOpenIDArgs({
            'foo': 'amsigned',
            'bar': 'notsigned',
            'azu': 'alsosigned',
            })
        sresponse = self.signatory.sign(response)

        new_assoc_handle = sresponse.fields.getArg(OPENID_NS, 'assoc_handle')
        self.failUnless(new_assoc_handle)
        self.failIfEqual(new_assoc_handle, assoc_handle)

        self.failUnlessEqual(
            sresponse.fields.getArg(OPENID_NS, 'invalidate_handle'),
            assoc_handle)

        self.failUnlessEqual(
            sresponse.fields.getArg(OPENID_NS, 'signed'), 'assoc_handle,azu,bar,foo,invalidate_handle,signed')
        self.failUnless(sresponse.fields.getArg(OPENID_NS, 'sig'))

        # make sure the new key is a dumb mode association
        self.failUnless(self.store.getAssociation(self._dumb_key, new_assoc_handle))
        self.failIf(self.store.getAssociation(self._normal_key, new_assoc_handle))
        self.failIf(self.messages, self.messages)


    def test_verify(self):
        assoc_handle = '{vroom}{zoom}'
        assoc = association.Association.fromExpiresIn(
            60, assoc_handle, 'sekrit', 'HMAC-SHA1')

        self.store.storeAssociation(self._dumb_key, assoc)

        signed = Message.fromPostArgs({
            'openid.foo': 'bar',
            'openid.apple': 'orange',
            'openid.assoc_handle': assoc_handle,
            'openid.signed': 'apple,assoc_handle,foo,signed',
            'openid.sig': 'uXoT1qm62/BB09Xbj98TQ8mlBco=',
            })

        verified = self.signatory.verify(assoc_handle, signed)
        self.failIf(self.messages, self.messages)
        self.failUnless(verified)


    def test_verifyBadSig(self):
        assoc_handle = '{vroom}{zoom}'
        assoc = association.Association.fromExpiresIn(
            60, assoc_handle, 'sekrit', 'HMAC-SHA1')

        self.store.storeAssociation(self._dumb_key, assoc)

        signed = Message.fromPostArgs({
            'openid.foo': 'bar',
            'openid.apple': 'orange',
            'openid.assoc_handle': assoc_handle,
            'openid.signed': 'apple,assoc_handle,foo,signed',
            'openid.sig': 'uXoT1qm62/BB09Xbj98TQ8mlBco='.encode('rot13'),
            })

        verified = self.signatory.verify(assoc_handle, signed)
        self.failIf(self.messages, self.messages)
        self.failIf(verified)

    def test_verifyBadHandle(self):
        assoc_handle = '{vroom}{zoom}'
        signed = Message.fromPostArgs({
            'foo': 'bar',
            'apple': 'orange',
            'openid.sig': "Ylu0KcIR7PvNegB/K41KpnRgJl0=",
            })

        verified = self.signatory.verify(assoc_handle, signed)
        self.failIf(verified)
        self.failUnless(self.messages)


    def test_verifyAssocMismatch(self):
        """Attempt to validate sign-all message with a signed-list assoc."""
        assoc_handle = '{vroom}{zoom}'
        assoc = association.Association.fromExpiresIn(
            60, assoc_handle, 'sekrit', 'HMAC-SHA1')

        self.store.storeAssociation(self._dumb_key, assoc)

        signed = Message.fromPostArgs({
            'foo': 'bar',
            'apple': 'orange',
            'openid.sig': "d71xlHtqnq98DonoSgoK/nD+QRM=",
            })

        verified = self.signatory.verify(assoc_handle, signed)
        self.failIf(verified)
        self.failUnless(self.messages)

    def test_getAssoc(self):
        assoc_handle = self.makeAssoc(dumb=True)
        assoc = self.signatory.getAssociation(assoc_handle, True)
        self.failUnless(assoc)
        self.failUnlessEqual(assoc.handle, assoc_handle)
        self.failIf(self.messages, self.messages)

    def test_getAssocExpired(self):
        assoc_handle = self.makeAssoc(dumb=True, lifetime=-10)
        assoc = self.signatory.getAssociation(assoc_handle, True)
        self.failIf(assoc, assoc)
        self.failUnless(self.messages)

    def test_getAssocInvalid(self):
        ah = 'no-such-handle'
        self.failUnlessEqual(
            self.signatory.getAssociation(ah, dumb=False), None)
        self.failIf(self.messages, self.messages)

    def test_getAssocDumbVsNormal(self):
        """getAssociation(dumb=False) cannot get a dumb assoc"""
        assoc_handle = self.makeAssoc(dumb=True)
        self.failUnlessEqual(
            self.signatory.getAssociation(assoc_handle, dumb=False), None)
        self.failIf(self.messages, self.messages)

    def test_getAssocNormalVsDumb(self):
        """getAssociation(dumb=True) cannot get a shared assoc

        From "Verifying Directly with the OpenID Provider"::

            An OP MUST NOT verify signatures for associations that have shared
            MAC keys.
        """
        assoc_handle = self.makeAssoc(dumb=False)
        self.failUnlessEqual(
            self.signatory.getAssociation(assoc_handle, dumb=True), None)
        self.failIf(self.messages, self.messages)

    def test_createAssociation(self):
        assoc = self.signatory.createAssociation(dumb=False)
        self.failUnless(self.signatory.getAssociation(assoc.handle, dumb=False))
        self.failIf(self.messages, self.messages)

    def makeAssoc(self, dumb, lifetime=60):
        assoc_handle = '{bling}'
        assoc = association.Association.fromExpiresIn(lifetime, assoc_handle,
                                                      'sekrit', 'HMAC-SHA1')

        self.store.storeAssociation((dumb and self._dumb_key) or self._normal_key, assoc)
        return assoc_handle

    def test_invalidate(self):
        assoc_handle = '-squash-'
        assoc = association.Association.fromExpiresIn(60, assoc_handle,
                                                      'sekrit', 'HMAC-SHA1')

        self.store.storeAssociation(self._dumb_key, assoc)
        assoc = self.signatory.getAssociation(assoc_handle, dumb=True)
        self.failUnless(assoc)
        assoc = self.signatory.getAssociation(assoc_handle, dumb=True)
        self.failUnless(assoc)
        self.signatory.invalidate(assoc_handle, dumb=True)
        assoc = self.signatory.getAssociation(assoc_handle, dumb=True)
        self.failIf(assoc)
        self.failIf(self.messages, self.messages)



if __name__ == '__main__':
    unittest.main()
