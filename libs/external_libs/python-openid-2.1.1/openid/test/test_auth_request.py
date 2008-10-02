import cgi
import unittest

from openid.consumer import consumer
from openid import message
from openid.test import support

class DummyEndpoint(object):
    preferred_namespace = None
    local_id = None
    server_url = None
    is_op_identifier = False

    def preferredNamespace(self):
        return self.preferred_namespace

    def getLocalID(self):
        return self.local_id

    def isOPIdentifier(self):
        return self.is_op_identifier

class DummyAssoc(object):
    handle = "assoc-handle"

class TestAuthRequestMixin(support.OpenIDTestMixin):
    """Mixin for AuthRequest tests for OpenID 1 and 2; DON'T add
    unittest.TestCase as a base class here."""

    preferred_namespace = None
    immediate = False
    expected_mode = 'checkid_setup'

    def setUp(self):
        self.endpoint = DummyEndpoint()
        self.endpoint.local_id = 'http://server.unittest/joe'
        self.endpoint.claimed_id = 'http://joe.vanity.example/'
        self.endpoint.server_url = 'http://server.unittest/'
        self.endpoint.preferred_namespace = self.preferred_namespace
        self.realm = 'http://example/'
        self.return_to = 'http://example/return/'
        self.assoc = DummyAssoc()
        self.authreq = consumer.AuthRequest(self.endpoint, self.assoc)

    def failUnlessAnonymous(self, msg):
        for key in ['claimed_id', 'identity']:
            self.failIfOpenIDKeyExists(msg, key)

    def failUnlessHasRequiredFields(self, msg):
        self.failUnlessEqual(self.preferred_namespace,
                             self.authreq.message.getOpenIDNamespace())

        self.failUnlessEqual(self.preferred_namespace,
                             msg.getOpenIDNamespace())

        self.failUnlessOpenIDValueEquals(msg, 'mode',
                                         self.expected_mode)

        # Implement these in subclasses because they depend on
        # protocol differences!
        self.failUnlessHasRealm(msg)
        self.failUnlessIdentifiersPresent(msg)

    # TESTS

    def test_checkNoAssocHandle(self):
        self.authreq.assoc = None
        msg = self.authreq.getMessage(self.realm, self.return_to,
                                      self.immediate)

        self.failIfOpenIDKeyExists(msg, 'assoc_handle')

    def test_checkWithAssocHandle(self):
        msg = self.authreq.getMessage(self.realm, self.return_to,
                                      self.immediate)

        self.failUnlessOpenIDValueEquals(msg, 'assoc_handle',
                                         self.assoc.handle)

    def test_addExtensionArg(self):
        self.authreq.addExtensionArg('bag:', 'color', 'brown')
        self.authreq.addExtensionArg('bag:', 'material', 'paper')
        self.failUnless('bag:' in self.authreq.message.namespaces)
        self.failUnlessEqual(self.authreq.message.getArgs('bag:'),
                             {'color': 'brown',
                              'material': 'paper'})
        msg = self.authreq.getMessage(self.realm, self.return_to,
                                      self.immediate)

        # XXX: this depends on the way that Message assigns
        # namespaces. Really it doesn't care that it has alias "0",
        # but that is tested anyway
        post_args = msg.toPostArgs()
        self.failUnlessEqual('brown', post_args['openid.ext0.color'])
        self.failUnlessEqual('paper', post_args['openid.ext0.material'])

    def test_standard(self):
        msg = self.authreq.getMessage(self.realm, self.return_to,
                                      self.immediate)

        self.failUnlessHasIdentifiers(
            msg, self.endpoint.local_id, self.endpoint.claimed_id)

class TestAuthRequestOpenID2(TestAuthRequestMixin, unittest.TestCase):
    preferred_namespace = message.OPENID2_NS

    def failUnlessHasRealm(self, msg):
        # check presence of proper realm key and absence of the wrong
        # one.
        self.failUnlessOpenIDValueEquals(msg, 'realm', self.realm)
        self.failIfOpenIDKeyExists(msg, 'trust_root')

    def failUnlessIdentifiersPresent(self, msg):
        identity_present = msg.hasKey(message.OPENID_NS, 'identity')
        claimed_present = msg.hasKey(message.OPENID_NS, 'claimed_id')

        self.failUnlessEqual(claimed_present, identity_present)

    def failUnlessHasIdentifiers(self, msg, op_specific_id, claimed_id):
        self.failUnlessOpenIDValueEquals(msg, 'identity', op_specific_id)
        self.failUnlessOpenIDValueEquals(msg, 'claimed_id', claimed_id)

    # TESTS

    def test_setAnonymousWorksForOpenID2(self):
        """OpenID AuthRequests should be able to set 'anonymous' to true."""
        self.failUnless(self.authreq.message.isOpenID2())
        self.authreq.setAnonymous(True)
        self.authreq.setAnonymous(False)

    def test_userAnonymousIgnoresIdentfier(self):
        self.authreq.setAnonymous(True)
        msg = self.authreq.getMessage(self.realm, self.return_to,
                                      self.immediate)
        self.failUnlessHasRequiredFields(msg)
        self.failUnlessAnonymous(msg)

    def test_opAnonymousIgnoresIdentifier(self):
        self.endpoint.is_op_identifier = True
        self.authreq.setAnonymous(True)
        msg = self.authreq.getMessage(self.realm, self.return_to,
                                      self.immediate)
        self.failUnlessHasRequiredFields(msg)
        self.failUnlessAnonymous(msg)

    def test_opIdentifierSendsIdentifierSelect(self):
        self.endpoint.is_op_identifier = True
        msg = self.authreq.getMessage(self.realm, self.return_to,
                                      self.immediate)
        self.failUnlessHasRequiredFields(msg)
        self.failUnlessHasIdentifiers(
            msg, message.IDENTIFIER_SELECT, message.IDENTIFIER_SELECT)

class TestAuthRequestOpenID1(TestAuthRequestMixin, unittest.TestCase):
    preferred_namespace = message.OPENID1_NS

    def setUpEndpoint(self):
        TestAuthRequestBase.setUpEndpoint(self)
        self.endpoint.preferred_namespace = message.OPENID1_NS

    def failUnlessHasIdentifiers(self, msg, op_specific_id, claimed_id):
        """Make sure claimed_is is *absent* in request."""
        self.failUnlessOpenIDValueEquals(msg, 'identity', op_specific_id)
        self.failIfOpenIDKeyExists(msg, 'claimed_id')

    def failUnlessIdentifiersPresent(self, msg):
        self.failIfOpenIDKeyExists(msg, 'claimed_id')
        self.failUnless(msg.hasKey(message.OPENID_NS, 'identity'))

    def failUnlessHasRealm(self, msg):
        # check presence of proper realm key and absence of the wrong
        # one.
        self.failUnlessOpenIDValueEquals(msg, 'trust_root', self.realm)
        self.failIfOpenIDKeyExists(msg, 'realm')

    # TESTS

    def test_setAnonymousFailsForOpenID1(self):
        """OpenID 1 requests MUST NOT be able to set anonymous to True"""
        self.failUnless(self.authreq.message.isOpenID1())
        self.failUnlessRaises(ValueError, self.authreq.setAnonymous, True)
        self.authreq.setAnonymous(False)

    def test_identifierSelect(self):
        """Identfier select SHOULD NOT be sent, but this pathway is in
        here in case some special discovery stuff is done to trigger
        it with OpenID 1. If it is triggered, it will send
        identifier_select just like OpenID 2.
        """
        self.endpoint.is_op_identifier = True
        msg = self.authreq.getMessage(self.realm, self.return_to,
                                      self.immediate)
        self.failUnlessHasRequiredFields(msg)
        self.failUnlessEqual(message.IDENTIFIER_SELECT,
                             msg.getArg(message.OPENID1_NS, 'identity'))

class TestAuthRequestOpenID1Immediate(TestAuthRequestOpenID1):
    immediate = True
    expected_mode = 'checkid_immediate'

class TestAuthRequestOpenID2Immediate(TestAuthRequestOpenID2):
    immediate = True
    expected_mode = 'checkid_immediate'

if __name__ == '__main__':
    unittest.main()
