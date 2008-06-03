from openid.test import datadriven

import unittest

from openid.message import Message, BARE_NS, OPENID_NS, OPENID2_NS
from openid import association
import time
from openid import cryptutil
import warnings

class AssociationSerializationTest(unittest.TestCase):
    def test_roundTrip(self):
        issued = int(time.time())
        lifetime = 600
        assoc = association.Association(
            'handle', 'secret', issued, lifetime, 'HMAC-SHA1')
        s = assoc.serialize()
        assoc2 = association.Association.deserialize(s)
        self.failUnlessEqual(assoc.handle, assoc2.handle)
        self.failUnlessEqual(assoc.issued, assoc2.issued)
        self.failUnlessEqual(assoc.secret, assoc2.secret)
        self.failUnlessEqual(assoc.lifetime, assoc2.lifetime)
        self.failUnlessEqual(assoc.assoc_type, assoc2.assoc_type)

from openid.server.server import \
     DiffieHellmanSHA1ServerSession, \
     DiffieHellmanSHA256ServerSession, \
     PlainTextServerSession

from openid.consumer.consumer import \
     DiffieHellmanSHA1ConsumerSession, \
     DiffieHellmanSHA256ConsumerSession, \
     PlainTextConsumerSession

from openid.dh import DiffieHellman

def createNonstandardConsumerDH():
    nonstandard_dh = DiffieHellman(1315291, 2)
    return DiffieHellmanSHA1ConsumerSession(nonstandard_dh)

class DiffieHellmanSessionTest(datadriven.DataDrivenTestCase):
    secrets = [
        '\x00' * 20,
        '\xff' * 20,
        ' ' * 20,
        'This is a secret....',
        ]

    session_factories = [
        (DiffieHellmanSHA1ConsumerSession, DiffieHellmanSHA1ServerSession),
        (createNonstandardConsumerDH, DiffieHellmanSHA1ServerSession),
        (PlainTextConsumerSession, PlainTextServerSession),
        ]

    def generateCases(cls):
        return [(c, s, sec)
                for c, s in cls.session_factories
                for sec in cls.secrets]

    generateCases = classmethod(generateCases)

    def __init__(self, csess_fact, ssess_fact, secret):
        datadriven.DataDrivenTestCase.__init__(self, csess_fact.__name__)
        self.secret = secret
        self.csess_fact = csess_fact
        self.ssess_fact = ssess_fact

    def runOneTest(self):
        csess = self.csess_fact()
        msg = Message.fromOpenIDArgs(csess.getRequest())
        ssess = self.ssess_fact.fromMessage(msg)
        check_secret = csess.extractSecret(
            Message.fromOpenIDArgs(ssess.answer(self.secret)))
        self.failUnlessEqual(self.secret, check_secret)



class TestMakePairs(unittest.TestCase):
    """Check the key-value formatting methods of associations.
    """

    def setUp(self):
        self.message = m = Message(OPENID2_NS)
        m.updateArgs(OPENID2_NS, {
            'mode': 'id_res',
            'identifier': '=example',
            'signed': 'identifier,mode',
            'sig': 'cephalopod',
            })
        m.updateArgs(BARE_NS, {'xey': 'value'})
        self.assoc = association.Association.fromExpiresIn(
            3600, '{sha1}', 'very_secret', "HMAC-SHA1")


    def testMakePairs(self):
        """Make pairs using the OpenID 1.x type signed list."""
        pairs = self.assoc._makePairs(self.message)
        expected = [
            ('identifier', '=example'),
            ('mode', 'id_res'),
            ]
        self.failUnlessEqual(pairs, expected)



class TestMac(unittest.TestCase):
    def setUp(self):
        self.pairs = [('key1', 'value1'),
                      ('key2', 'value2')]


    def test_sha1(self):
        assoc = association.Association.fromExpiresIn(
            3600, '{sha1}', 'very_secret', "HMAC-SHA1")
        expected = ('\xe0\x1bv\x04\xf1G\xc0\xbb\x7f\x9a\x8b'
                    '\xe9\xbc\xee}\\\xe5\xbb7*')
        sig = assoc.sign(self.pairs)
        self.failUnlessEqual(sig, expected)

    if cryptutil.SHA256_AVAILABLE:
        def test_sha256(self):
            assoc = association.Association.fromExpiresIn(
                3600, '{sha256SA}', 'very_secret', "HMAC-SHA256")
            expected = ('\xfd\xaa\xfe;\xac\xfc*\x988\xad\x05d6-\xeaVy'
                        '\xd5\xa5Z.<\xa9\xed\x18\x82\\$\x95x\x1c&')
            sig = assoc.sign(self.pairs)
            self.failUnlessEqual(sig, expected)



class TestMessageSigning(unittest.TestCase):
    def setUp(self):
        self.message = m = Message(OPENID2_NS)
        m.updateArgs(OPENID2_NS, {'mode': 'id_res',
                                  'identifier': '=example'})
        m.updateArgs(BARE_NS, {'xey': 'value'})
        self.args = {'openid.mode': 'id_res',
                     'openid.identifier': '=example',
                     'xey': 'value'}


    def test_signSHA1(self):
        assoc = association.Association.fromExpiresIn(
            3600, '{sha1}', 'very_secret', "HMAC-SHA1")
        signed = assoc.signMessage(self.message)
        self.failUnless(signed.getArg(OPENID_NS, "sig"))
        self.failUnlessEqual(signed.getArg(OPENID_NS, "signed"),
                             "assoc_handle,identifier,mode,ns,signed")
        self.failUnlessEqual(signed.getArg(BARE_NS, "xey"), "value",
                             signed)

    if cryptutil.SHA256_AVAILABLE:
        def test_signSHA256(self):
            assoc = association.Association.fromExpiresIn(
                3600, '{sha1}', 'very_secret', "HMAC-SHA256")
            signed = assoc.signMessage(self.message)
            self.failUnless(signed.getArg(OPENID_NS, "sig"))
            self.failUnlessEqual(signed.getArg(OPENID_NS, "signed"),
                                 "assoc_handle,identifier,mode,ns,signed")
            self.failUnlessEqual(signed.getArg(BARE_NS, "xey"), "value",
                                 signed)


class TestCheckMessageSignature(unittest.TestCase):
    def test_aintGotSignedList(self):
        m = Message(OPENID2_NS)
        m.updateArgs(OPENID2_NS, {'mode': 'id_res',
                                  'identifier': '=example',
                                  'sig': 'coyote',
                                  })
        m.updateArgs(BARE_NS, {'xey': 'value'})
        assoc = association.Association.fromExpiresIn(
            3600, '{sha1}', 'very_secret', "HMAC-SHA1")
        self.failUnlessRaises(ValueError, assoc.checkMessageSignature, m)


def pyUnitTests():
    return datadriven.loadTests(__name__)

if __name__ == '__main__':
    suite = pyUnitTests()
    runner = unittest.TextTestRunner()
    runner.run(suite)
