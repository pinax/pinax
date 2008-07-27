from openid.extensions import sreg
from openid.message import NamespaceMap, Message, registerNamespaceAlias
from openid.server.server import OpenIDRequest, OpenIDResponse

import unittest

class SRegURITest(unittest.TestCase):
    def test_is11(self):
        self.failUnlessEqual(sreg.ns_uri_1_1, sreg.ns_uri)

class CheckFieldNameTest(unittest.TestCase):
    def test_goodNamePasses(self):
        for field_name in sreg.data_fields:
            sreg.checkFieldName(field_name)

    def test_badNameFails(self):
        self.failUnlessRaises(ValueError, sreg.checkFieldName, 'INVALID')

    def test_badTypeFails(self):
        self.failUnlessRaises(ValueError, sreg.checkFieldName, None)

# For supportsSReg test
class FakeEndpoint(object):
    def __init__(self, supported):
        self.supported = supported
        self.checked_uris = []

    def usesExtension(self, namespace_uri):
        self.checked_uris.append(namespace_uri)
        return namespace_uri in self.supported

class SupportsSRegTest(unittest.TestCase):
    def test_unsupported(self):
        endpoint = FakeEndpoint([])
        self.failIf(sreg.supportsSReg(endpoint))
        self.failUnlessEqual([sreg.ns_uri_1_1, sreg.ns_uri_1_0],
                             endpoint.checked_uris)

    def test_supported_1_1(self):
        endpoint = FakeEndpoint([sreg.ns_uri_1_1])
        self.failUnless(sreg.supportsSReg(endpoint))
        self.failUnlessEqual([sreg.ns_uri_1_1], endpoint.checked_uris)

    def test_supported_1_0(self):
        endpoint = FakeEndpoint([sreg.ns_uri_1_0])
        self.failUnless(sreg.supportsSReg(endpoint))
        self.failUnlessEqual([sreg.ns_uri_1_1, sreg.ns_uri_1_0],
                             endpoint.checked_uris)

class FakeMessage(object):
    def __init__(self):
        self.openid1 = False
        self.namespaces = NamespaceMap()

    def isOpenID1(self):
        return self.openid1

class GetNSTest(unittest.TestCase):
    def setUp(self):
        self.msg = FakeMessage()

    def test_openID2Empty(self):
        ns_uri = sreg.getSRegNS(self.msg)
        self.failUnlessEqual(self.msg.namespaces.getAlias(ns_uri), 'sreg')
        self.failUnlessEqual(sreg.ns_uri, ns_uri)

    def test_openID1Empty(self):
        self.msg.openid1 = True
        ns_uri = sreg.getSRegNS(self.msg)
        self.failUnlessEqual(self.msg.namespaces.getAlias(ns_uri), 'sreg')
        self.failUnlessEqual(sreg.ns_uri, ns_uri)

    def test_openID1Defined_1_0(self):
        self.msg.openid1 = True
        self.msg.namespaces.add(sreg.ns_uri_1_0)
        ns_uri = sreg.getSRegNS(self.msg)
        self.failUnlessEqual(sreg.ns_uri_1_0, ns_uri)

    def test_openID1Defined_1_0_overrideAlias(self):
        for openid_version in [True, False]:
            for sreg_version in [sreg.ns_uri_1_0, sreg.ns_uri_1_1]:
                for alias in ['sreg', 'bogus']:
                    self.setUp()

                    self.msg.openid1 = openid_version
                    self.msg.namespaces.addAlias(sreg_version, alias)
                    ns_uri = sreg.getSRegNS(self.msg)
                    self.failUnlessEqual(self.msg.namespaces.getAlias(ns_uri), alias)
                    self.failUnlessEqual(sreg_version, ns_uri)

    def test_openID1DefinedBadly(self):
        self.msg.openid1 = True
        self.msg.namespaces.addAlias('http://invalid/', 'sreg')
        self.failUnlessRaises(sreg.SRegNamespaceError,
                              sreg.getSRegNS, self.msg)

    def test_openID2DefinedBadly(self):
        self.msg.openid1 = False
        self.msg.namespaces.addAlias('http://invalid/', 'sreg')
        self.failUnlessRaises(sreg.SRegNamespaceError,
                              sreg.getSRegNS, self.msg)

    def test_openID2Defined_1_0(self):
        self.msg.namespaces.add(sreg.ns_uri_1_0)
        ns_uri = sreg.getSRegNS(self.msg)
        self.failUnlessEqual(sreg.ns_uri_1_0, ns_uri)

    def test_openID1_sregNSfromArgs(self):
        args = {
            'sreg.optional': 'nickname',
            'sreg.required': 'dob',
            }

        m = Message.fromOpenIDArgs(args)

        self.failUnless(m.getArg(sreg.ns_uri_1_1, 'optional') == 'nickname')
        self.failUnless(m.getArg(sreg.ns_uri_1_1, 'required') == 'dob')

class SRegRequestTest(unittest.TestCase):
    def test_constructEmpty(self):
        req = sreg.SRegRequest()
        self.failUnlessEqual([], req.optional)
        self.failUnlessEqual([], req.required)
        self.failUnlessEqual(None, req.policy_url)
        self.failUnlessEqual(sreg.ns_uri, req.ns_uri)

    def test_constructFields(self):
        req = sreg.SRegRequest(
            ['nickname'],
            ['gender'],
            'http://policy',
            'http://sreg.ns_uri')
        self.failUnlessEqual(['gender'], req.optional)
        self.failUnlessEqual(['nickname'], req.required)
        self.failUnlessEqual('http://policy', req.policy_url)
        self.failUnlessEqual('http://sreg.ns_uri', req.ns_uri)

    def test_constructBadFields(self):
        self.failUnlessRaises(
            ValueError,
            sreg.SRegRequest, ['elvis'])

    def test_fromOpenIDRequest(self):
        args = {}
        ns_sentinel = object()
        args_sentinel = object()

        class FakeMessage(object):
            copied = False

            def __init__(self):
                self.message = Message()

            def getArgs(msg_self, ns_uri):
                self.failUnlessEqual(ns_sentinel, ns_uri)
                return args_sentinel

            def copy(msg_self):
                msg_self.copied = True
                return msg_self

        class TestingReq(sreg.SRegRequest):
            def _getSRegNS(req_self, unused):
                return ns_sentinel

            def parseExtensionArgs(req_self, args):
                self.failUnlessEqual(args_sentinel, args)

        openid_req = OpenIDRequest()

        msg = FakeMessage()
        openid_req.message = msg

        req = TestingReq.fromOpenIDRequest(openid_req)
        self.failUnless(type(req) is TestingReq)
        self.failUnless(msg.copied)

    def test_parseExtensionArgs_empty(self):
        req = sreg.SRegRequest()
        results = req.parseExtensionArgs({})
        self.failUnlessEqual(None, results)

    def test_parseExtensionArgs_extraIgnored(self):
        req = sreg.SRegRequest()
        req.parseExtensionArgs({'janrain':'inc'})

    def test_parseExtensionArgs_nonStrict(self):
        req = sreg.SRegRequest()
        req.parseExtensionArgs({'required':'beans'})
        self.failUnlessEqual([], req.required)

    def test_parseExtensionArgs_strict(self):
        req = sreg.SRegRequest()
        self.failUnlessRaises(
            ValueError,
            req.parseExtensionArgs, {'required':'beans'}, strict=True)

    def test_parseExtensionArgs_policy(self):
        req = sreg.SRegRequest()
        req.parseExtensionArgs({'policy_url':'http://policy'}, strict=True)
        self.failUnlessEqual('http://policy', req.policy_url)

    def test_parseExtensionArgs_requiredEmpty(self):
        req = sreg.SRegRequest()
        req.parseExtensionArgs({'required':''}, strict=True)
        self.failUnlessEqual([], req.required)

    def test_parseExtensionArgs_optionalEmpty(self):
        req = sreg.SRegRequest()
        req.parseExtensionArgs({'optional':''}, strict=True)
        self.failUnlessEqual([], req.optional)

    def test_parseExtensionArgs_optionalSingle(self):
        req = sreg.SRegRequest()
        req.parseExtensionArgs({'optional':'nickname'}, strict=True)
        self.failUnlessEqual(['nickname'], req.optional)

    def test_parseExtensionArgs_optionalList(self):
        req = sreg.SRegRequest()
        req.parseExtensionArgs({'optional':'nickname,email'}, strict=True)
        self.failUnlessEqual(['nickname','email'], req.optional)

    def test_parseExtensionArgs_optionalListBadNonStrict(self):
        req = sreg.SRegRequest()
        req.parseExtensionArgs({'optional':'nickname,email,beer'})
        self.failUnlessEqual(['nickname','email'], req.optional)

    def test_parseExtensionArgs_optionalListBadStrict(self):
        req = sreg.SRegRequest()
        self.failUnlessRaises(
            ValueError,
            req.parseExtensionArgs, {'optional':'nickname,email,beer'},
            strict=True)

    def test_parseExtensionArgs_bothNonStrict(self):
        req = sreg.SRegRequest()
        req.parseExtensionArgs({'optional':'nickname',
                                'required':'nickname'})
        self.failUnlessEqual([], req.optional)
        self.failUnlessEqual(['nickname'], req.required)

    def test_parseExtensionArgs_bothStrict(self):
        req = sreg.SRegRequest()
        self.failUnlessRaises(
            ValueError,
            req.parseExtensionArgs,
            {'optional':'nickname',
             'required':'nickname'},
            strict=True)

    def test_parseExtensionArgs_bothList(self):
        req = sreg.SRegRequest()
        req.parseExtensionArgs({'optional':'nickname,email',
                                'required':'country,postcode'}, strict=True)
        self.failUnlessEqual(['nickname','email'], req.optional)
        self.failUnlessEqual(['country','postcode'], req.required)

    def test_allRequestedFields(self):
        req = sreg.SRegRequest()
        self.failUnlessEqual([], req.allRequestedFields())
        req.requestField('nickname')
        self.failUnlessEqual(['nickname'], req.allRequestedFields())
        req.requestField('gender', required=True)
        requested = req.allRequestedFields()
        requested.sort()
        self.failUnlessEqual(['gender', 'nickname'], requested)

    def test_wereFieldsRequested(self):
        req = sreg.SRegRequest()
        self.failIf(req.wereFieldsRequested())
        req.requestField('gender')
        self.failUnless(req.wereFieldsRequested())

    def test_contains(self):
        req = sreg.SRegRequest()
        for field_name in sreg.data_fields:
            self.failIf(field_name in req)

        self.failIf('something else' in req)

        req.requestField('nickname')
        for field_name in sreg.data_fields:
            if field_name == 'nickname':
                self.failUnless(field_name in req)
            else:
                self.failIf(field_name in req)

    def test_requestField_bogus(self):
        req = sreg.SRegRequest()
        self.failUnlessRaises(
            ValueError,
            req.requestField, 'something else')

        self.failUnlessRaises(
            ValueError,
            req.requestField, 'something else', strict=True)

    def test_requestField(self):
        # Add all of the fields, one at a time
        req = sreg.SRegRequest()
        fields = list(sreg.data_fields)
        for field_name in fields:
            req.requestField(field_name)

        self.failUnlessEqual(fields, req.optional)
        self.failUnlessEqual([], req.required)

        # By default, adding the same fields over again has no effect
        for field_name in fields:
            req.requestField(field_name)

        self.failUnlessEqual(fields, req.optional)
        self.failUnlessEqual([], req.required)

        # Requesting a field as required overrides requesting it as optional
        expected = list(fields)
        overridden = expected.pop(0)
        req.requestField(overridden, required=True)
        self.failUnlessEqual(expected, req.optional)
        self.failUnlessEqual([overridden], req.required)

        # Requesting a field as required overrides requesting it as optional
        for field_name in fields:
            req.requestField(field_name, required=True)

        self.failUnlessEqual([], req.optional)
        self.failUnlessEqual(fields, req.required)

        # Requesting it as optional does not downgrade it to optional
        for field_name in fields:
            req.requestField(field_name)

        self.failUnlessEqual([], req.optional)
        self.failUnlessEqual(fields, req.required)

    def test_requestFields_type(self):
        req = sreg.SRegRequest()
        self.failUnlessRaises(TypeError, req.requestFields, 'nickname')

    def test_requestFields(self):
        # Add all of the fields
        req = sreg.SRegRequest()

        fields = list(sreg.data_fields)
        req.requestFields(fields)

        self.failUnlessEqual(fields, req.optional)
        self.failUnlessEqual([], req.required)

        # By default, adding the same fields over again has no effect
        req.requestFields(fields)

        self.failUnlessEqual(fields, req.optional)
        self.failUnlessEqual([], req.required)

        # Requesting a field as required overrides requesting it as optional
        expected = list(fields)
        overridden = expected.pop(0)
        req.requestFields([overridden], required=True)
        self.failUnlessEqual(expected, req.optional)
        self.failUnlessEqual([overridden], req.required)

        # Requesting a field as required overrides requesting it as optional
        req.requestFields(fields, required=True)

        self.failUnlessEqual([], req.optional)
        self.failUnlessEqual(fields, req.required)

        # Requesting it as optional does not downgrade it to optional
        req.requestFields(fields)

        self.failUnlessEqual([], req.optional)
        self.failUnlessEqual(fields, req.required)

    def test_getExtensionArgs(self):
        req = sreg.SRegRequest()
        self.failUnlessEqual({}, req.getExtensionArgs())

        req.requestField('nickname')
        self.failUnlessEqual({'optional':'nickname'}, req.getExtensionArgs())

        req.requestField('email')
        self.failUnlessEqual({'optional':'nickname,email'},
                             req.getExtensionArgs())

        req.requestField('gender', required=True)
        self.failUnlessEqual({'optional':'nickname,email',
                              'required':'gender'},
                             req.getExtensionArgs())

        req.requestField('postcode', required=True)
        self.failUnlessEqual({'optional':'nickname,email',
                              'required':'gender,postcode'},
                             req.getExtensionArgs())

        req.policy_url = 'http://policy.invalid/'
        self.failUnlessEqual({'optional':'nickname,email',
                              'required':'gender,postcode',
                              'policy_url':'http://policy.invalid/'},
                             req.getExtensionArgs())

data = {
    'nickname':'linusaur',
    'postcode':'12345',
    'country':'US',
    'gender':'M',
    'fullname':'Leonhard Euler',
    'email':'president@whitehouse.gov',
    'dob':'0000-00-00',
    'language':'en-us',
    }

class DummySuccessResponse(object):
    def __init__(self, message, signed_stuff):
        self.message = message
        self.signed_stuff = signed_stuff

    def getSignedNS(self, ns_uri):
        return self.signed_stuff

class SRegResponseTest(unittest.TestCase):
    def test_construct(self):
        resp = sreg.SRegResponse(data)

        self.failUnless(resp)

        empty_resp = sreg.SRegResponse({})
        self.failIf(empty_resp)

        # XXX: finish this test

    def test_fromSuccessResponse_signed(self):
        message = Message.fromOpenIDArgs({
            'sreg.nickname':'The Mad Stork',
            })
        success_resp = DummySuccessResponse(message, {})
        sreg_resp = sreg.SRegResponse.fromSuccessResponse(success_resp)
        self.failIf(sreg_resp)

    def test_fromSuccessResponse_unsigned(self):
        message = Message.fromOpenIDArgs({
            'sreg.nickname':'The Mad Stork',
            })
        success_resp = DummySuccessResponse(message, {})
        sreg_resp = sreg.SRegResponse.fromSuccessResponse(success_resp,
                                                          signed_only=False)
        self.failUnlessEqual([('nickname', 'The Mad Stork')],
                             sreg_resp.items())

class SendFieldsTest(unittest.TestCase):
    def test(self):
        # Create a request message with simple registration fields
        sreg_req = sreg.SRegRequest(required=['nickname', 'email'],
                                    optional=['fullname'])
        req_msg = Message()
        req_msg.updateArgs(sreg.ns_uri, sreg_req.getExtensionArgs())

        req = OpenIDRequest()
        req.message = req_msg
        req.namespace = req_msg.getOpenIDNamespace()

        # -> send checkid_* request

        # Create an empty response message
        resp_msg = Message()
        resp = OpenIDResponse(req)
        resp.fields = resp_msg

        # Put the requested data fields in the response message
        sreg_resp = sreg.SRegResponse.extractResponse(sreg_req, data)
        resp.addExtension(sreg_resp)

        # <- send id_res response

        # Extract the fields that were sent
        sreg_data_resp = resp_msg.getArgs(sreg.ns_uri)
        self.failUnlessEqual(
            {'nickname':'linusaur',
             'email':'president@whitehouse.gov',
             'fullname':'Leonhard Euler',
             }, sreg_data_resp)

if __name__ == '__main__':
    unittest.main()
