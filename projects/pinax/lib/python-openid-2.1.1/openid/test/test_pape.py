
from openid.extensions import pape
from openid.message import *
from openid.server import server

import unittest

class PapeRequestTestCase(unittest.TestCase):
    def setUp(self):
        self.req = pape.Request()

    def test_construct(self):
        self.failUnlessEqual([], self.req.preferred_auth_policies)
        self.failUnlessEqual(None, self.req.max_auth_age)
        self.failUnlessEqual('pape', self.req.ns_alias)

        req2 = pape.Request([pape.AUTH_MULTI_FACTOR], 1000)
        self.failUnlessEqual([pape.AUTH_MULTI_FACTOR], req2.preferred_auth_policies)
        self.failUnlessEqual(1000, req2.max_auth_age)

    def test_add_policy_uri(self):
        self.failUnlessEqual([], self.req.preferred_auth_policies)
        self.req.addPolicyURI(pape.AUTH_MULTI_FACTOR)
        self.failUnlessEqual([pape.AUTH_MULTI_FACTOR], self.req.preferred_auth_policies)
        self.req.addPolicyURI(pape.AUTH_MULTI_FACTOR)
        self.failUnlessEqual([pape.AUTH_MULTI_FACTOR], self.req.preferred_auth_policies)
        self.req.addPolicyURI(pape.AUTH_PHISHING_RESISTANT)
        self.failUnlessEqual([pape.AUTH_MULTI_FACTOR, pape.AUTH_PHISHING_RESISTANT],
                             self.req.preferred_auth_policies)
        self.req.addPolicyURI(pape.AUTH_MULTI_FACTOR)
        self.failUnlessEqual([pape.AUTH_MULTI_FACTOR, pape.AUTH_PHISHING_RESISTANT],
                             self.req.preferred_auth_policies)

    def test_getExtensionArgs(self):
        self.failUnlessEqual({'preferred_auth_policies': ''}, self.req.getExtensionArgs())
        self.req.addPolicyURI('http://uri')
        self.failUnlessEqual({'preferred_auth_policies': 'http://uri'}, self.req.getExtensionArgs())
        self.req.addPolicyURI('http://zig')
        self.failUnlessEqual({'preferred_auth_policies': 'http://uri http://zig'}, self.req.getExtensionArgs())
        self.req.max_auth_age = 789
        self.failUnlessEqual({'preferred_auth_policies': 'http://uri http://zig', 'max_auth_age': '789'}, self.req.getExtensionArgs())

    def test_parseExtensionArgs(self):
        args = {'preferred_auth_policies': 'http://foo http://bar',
                'max_auth_age': '9'}
        self.req.parseExtensionArgs(args)
        self.failUnlessEqual(9, self.req.max_auth_age)
        self.failUnlessEqual(['http://foo','http://bar'], self.req.preferred_auth_policies)

    def test_parseExtensionArgs_empty(self):
        self.req.parseExtensionArgs({})
        self.failUnlessEqual(None, self.req.max_auth_age)
        self.failUnlessEqual([], self.req.preferred_auth_policies)

    def test_fromOpenIDRequest(self):
        openid_req_msg = Message.fromOpenIDArgs({
          'mode': 'checkid_setup',
          'ns': OPENID2_NS,
          'ns.pape': pape.ns_uri,
          'pape.preferred_auth_policies': ' '.join([pape.AUTH_MULTI_FACTOR, pape.AUTH_PHISHING_RESISTANT]),
          'pape.max_auth_age': '5476'
          })
        oid_req = server.OpenIDRequest()
        oid_req.message = openid_req_msg
        req = pape.Request.fromOpenIDRequest(oid_req)
        self.failUnlessEqual([pape.AUTH_MULTI_FACTOR, pape.AUTH_PHISHING_RESISTANT], req.preferred_auth_policies)
        self.failUnlessEqual(5476, req.max_auth_age)

    def test_fromOpenIDRequest_no_pape(self):
        message = Message()
        openid_req = server.OpenIDRequest()
        openid_req.message = message
        pape_req = pape.Request.fromOpenIDRequest(openid_req)
        assert(pape_req is None)

    def test_preferred_types(self):
        self.req.addPolicyURI(pape.AUTH_PHISHING_RESISTANT)
        self.req.addPolicyURI(pape.AUTH_MULTI_FACTOR)
        pt = self.req.preferredTypes([pape.AUTH_MULTI_FACTOR,
                                      pape.AUTH_MULTI_FACTOR_PHYSICAL])
        self.failUnlessEqual([pape.AUTH_MULTI_FACTOR], pt)

class DummySuccessResponse:
    def __init__(self, message, signed_stuff):
        self.message = message
        self.signed_stuff = signed_stuff

    def getSignedNS(self, ns_uri):
        return self.signed_stuff

class PapeResponseTestCase(unittest.TestCase):
    def setUp(self):
        self.req = pape.Response()

    def test_construct(self):
        self.failUnlessEqual([], self.req.auth_policies)
        self.failUnlessEqual(None, self.req.auth_age)
        self.failUnlessEqual('pape', self.req.ns_alias)
        self.failUnlessEqual(None, self.req.nist_auth_level)

        req2 = pape.Response([pape.AUTH_MULTI_FACTOR], 1000, 3)
        self.failUnlessEqual([pape.AUTH_MULTI_FACTOR], req2.auth_policies)
        self.failUnlessEqual(1000, req2.auth_age)
        self.failUnlessEqual(3, req2.nist_auth_level)

    def test_add_policy_uri(self):
        self.failUnlessEqual([], self.req.auth_policies)
        self.req.addPolicyURI(pape.AUTH_MULTI_FACTOR)
        self.failUnlessEqual([pape.AUTH_MULTI_FACTOR], self.req.auth_policies)
        self.req.addPolicyURI(pape.AUTH_MULTI_FACTOR)
        self.failUnlessEqual([pape.AUTH_MULTI_FACTOR], self.req.auth_policies)
        self.req.addPolicyURI(pape.AUTH_PHISHING_RESISTANT)
        self.failUnlessEqual([pape.AUTH_MULTI_FACTOR, pape.AUTH_PHISHING_RESISTANT], self.req.auth_policies)
        self.req.addPolicyURI(pape.AUTH_MULTI_FACTOR)
        self.failUnlessEqual([pape.AUTH_MULTI_FACTOR, pape.AUTH_PHISHING_RESISTANT], self.req.auth_policies)

    def test_getExtensionArgs(self):
        self.failUnlessEqual({'auth_policies': ''}, self.req.getExtensionArgs())
        self.req.addPolicyURI('http://uri')
        self.failUnlessEqual({'auth_policies': 'http://uri'}, self.req.getExtensionArgs())
        self.req.addPolicyURI('http://zig')
        self.failUnlessEqual({'auth_policies': 'http://uri http://zig'}, self.req.getExtensionArgs())
        self.req.auth_age = 789
        self.failUnlessEqual({'auth_policies': 'http://uri http://zig', 'auth_age': '789'}, self.req.getExtensionArgs())
        self.req.nist_auth_level = 3
        self.failUnlessEqual({'auth_policies': 'http://uri http://zig', 'auth_age': '789', 'nist_auth_level': '3'}, self.req.getExtensionArgs())

    def test_getExtensionArgs_error_auth_age(self):
        self.req.auth_age = "older than the sun"
        self.failUnlessRaises(ValueError, self.req.getExtensionArgs)
        self.req.auth_age = -10
        self.failUnlessRaises(ValueError, self.req.getExtensionArgs)

    def test_getExtensionArgs_error_nist_auth_level(self):
        self.req.nist_auth_level = "high as a kite"
        self.failUnlessRaises(ValueError, self.req.getExtensionArgs)
        self.req.nist_auth_level = 5
        self.failUnlessRaises(ValueError, self.req.getExtensionArgs)
        self.req.nist_auth_level = -1
        self.failUnlessRaises(ValueError, self.req.getExtensionArgs)

    def test_parseExtensionArgs(self):
        args = {'auth_policies': 'http://foo http://bar',
                'auth_age': '9'}
        self.req.parseExtensionArgs(args)
        self.failUnlessEqual(9, self.req.auth_age)
        self.failUnlessEqual(['http://foo','http://bar'], self.req.auth_policies)

    def test_parseExtensionArgs_empty(self):
        self.req.parseExtensionArgs({})
        self.failUnlessEqual(None, self.req.auth_age)
        self.failUnlessEqual([], self.req.auth_policies)
      
    def test_parseExtensionArgs_strict_bogus1(self):
        args = {'auth_policies': 'http://foo http://bar',
                'auth_age': 'not too old'}
        self.failUnlessRaises(ValueError, self.req.parseExtensionArgs,
                              args, True)

    def test_parseExtensionArgs_strict_bogus2(self):
        args = {'auth_policies': 'http://foo http://bar',
                'auth_age': '63',
                'nist_auth_level': 'some'}
        self.failUnlessRaises(ValueError, self.req.parseExtensionArgs,
                              args, True)
      
    def test_parseExtensionArgs_strict_good(self):
        args = {'auth_policies': 'http://foo http://bar',
                'auth_age': '0',
                'nist_auth_level': '0'}
        self.req.parseExtensionArgs(args, True)
        self.failUnlessEqual(['http://foo','http://bar'], self.req.auth_policies)
        self.failUnlessEqual(0, self.req.auth_age)
        self.failUnlessEqual(0, self.req.nist_auth_level)

    def test_parseExtensionArgs_nostrict_bogus(self):
        args = {'auth_policies': 'http://foo http://bar',
                'auth_age': 'old',
                'nist_auth_level': 'some'}
        self.req.parseExtensionArgs(args)
        self.failUnlessEqual(['http://foo','http://bar'], self.req.auth_policies)
        self.failUnlessEqual(None, self.req.auth_age)
        self.failUnlessEqual(None, self.req.nist_auth_level)

    def test_fromSuccessResponse(self):
        openid_req_msg = Message.fromOpenIDArgs({
          'mode': 'id_res',
          'ns': OPENID2_NS,
          'ns.pape': pape.ns_uri,
          'pape.auth_policies': ' '.join([pape.AUTH_MULTI_FACTOR, pape.AUTH_PHISHING_RESISTANT]),
          'pape.auth_age': '5476'
          })
        signed_stuff = {
          'auth_policies': ' '.join([pape.AUTH_MULTI_FACTOR, pape.AUTH_PHISHING_RESISTANT]),
          'auth_age': '5476'
        }
        oid_req = DummySuccessResponse(openid_req_msg, signed_stuff)
        req = pape.Response.fromSuccessResponse(oid_req)
        self.failUnlessEqual([pape.AUTH_MULTI_FACTOR, pape.AUTH_PHISHING_RESISTANT], req.auth_policies)
        self.failUnlessEqual(5476, req.auth_age)
