"""Tests for the attribute exchange extension module
"""

import unittest
from openid.extensions import ax
from openid.message import NamespaceMap, Message, OPENID2_NS
from openid.consumer.consumer import SuccessResponse

class BogusAXMessage(ax.AXMessage):
    mode = 'bogus'

    getExtensionArgs = ax.AXMessage._newArgs

class DummyRequest(object):
    def __init__(self, message):
        self.message = message

class AXMessageTest(unittest.TestCase):
    def setUp(self):
        self.bax = BogusAXMessage()

    def test_checkMode(self):
        check = self.bax._checkMode
        self.failUnlessRaises(ax.NotAXMessage, check, {})
        self.failUnlessRaises(ax.AXError, check, {'mode':'fetch_request'})

        # does not raise an exception when the mode is right
        check({'mode':self.bax.mode})

    def test_checkMode_newArgs(self):
        """_newArgs generates something that has the correct mode"""
        # This would raise AXError if it didn't like the mode newArgs made.
        self.bax._checkMode(self.bax._newArgs())


class AttrInfoTest(unittest.TestCase):
    def test_construct(self):
        self.failUnlessRaises(TypeError, ax.AttrInfo)
        type_uri = 'a uri'
        ainfo = ax.AttrInfo(type_uri)

        self.failUnlessEqual(type_uri, ainfo.type_uri)
        self.failUnlessEqual(1, ainfo.count)
        self.failIf(ainfo.required)
        self.failUnless(ainfo.alias is None)


class ToTypeURIsTest(unittest.TestCase):
    def setUp(self):
        self.aliases = NamespaceMap()

    def test_empty(self):
        for empty in [None, '']:
            uris = ax.toTypeURIs(self.aliases, empty)
            self.failUnlessEqual([], uris)

    def test_undefined(self):
        self.failUnlessRaises(
            KeyError,
            ax.toTypeURIs, self.aliases, 'http://janrain.com/')

    def test_one(self):
        uri = 'http://janrain.com/'
        alias = 'openid_hackers'
        self.aliases.addAlias(uri, alias)
        uris = ax.toTypeURIs(self.aliases, alias)
        self.failUnlessEqual([uri], uris)

    def test_two(self):
        uri1 = 'http://janrain.com/'
        alias1 = 'openid_hackers'
        self.aliases.addAlias(uri1, alias1)

        uri2 = 'http://jyte.com/'
        alias2 = 'openid_hack'
        self.aliases.addAlias(uri2, alias2)

        uris = ax.toTypeURIs(self.aliases, ','.join([alias1, alias2]))
        self.failUnlessEqual([uri1, uri2], uris)

class ParseAXValuesTest(unittest.TestCase):
    """Testing AXKeyValueMessage.parseExtensionArgs."""

    def failUnlessAXKeyError(self, ax_args):
        msg = ax.AXKeyValueMessage()
        self.failUnlessRaises(KeyError, msg.parseExtensionArgs, ax_args)

    def failUnlessAXValues(self, ax_args, expected_args):
        """Fail unless parseExtensionArgs(ax_args) == expected_args."""
        msg = ax.AXKeyValueMessage()
        msg.parseExtensionArgs(ax_args)
        self.failUnlessEqual(expected_args, msg.data)

    def test_emptyIsValid(self):
        self.failUnlessAXValues({}, {})

    def test_missingValueForAliasExplodes(self):
        self.failUnlessAXKeyError({'type.foo':'urn:foo'})

    def test_countPresentButNotValue(self):
        self.failUnlessAXKeyError({'type.foo':'urn:foo',
                                   'count.foo':'1'})

    def test_invalidCountValue(self):
        msg = ax.FetchRequest()
        self.failUnlessRaises(ax.AXError,
                              msg.parseExtensionArgs,
                              {'type.foo':'urn:foo',
                               'count.foo':'bogus'})

    def test_requestUnlimitedValues(self):
        msg = ax.FetchRequest()

        msg.parseExtensionArgs(
            {'mode':'fetch_request',
             'required':'foo',
             'type.foo':'urn:foo',
             'count.foo':ax.UNLIMITED_VALUES})

        attrs = list(msg.iterAttrs())
        foo = attrs[0]

        self.failUnless(foo.count == ax.UNLIMITED_VALUES)
        self.failUnless(foo.wantsUnlimitedValues())

    def test_longAlias(self):
        # Spec minimum length is 32 characters.  This is a silly test
        # for this library, but it's here for completeness.
        alias = 'x' * ax.MINIMUM_SUPPORTED_ALIAS_LENGTH

        msg = ax.AXKeyValueMessage()
        msg.parseExtensionArgs(
            {'type.%s' % (alias,): 'urn:foo',
             'count.%s' % (alias,): '1',
             'value.%s.1' % (alias,): 'first'}
            )

    def test_invalidAlias(self):
        types = [
            ax.AXKeyValueMessage,
            ax.FetchRequest
            ]

        inputs = [
            {'type.a.b':'urn:foo',
             'count.a.b':'1'},
            {'type.a,b':'urn:foo',
             'count.a,b':'1'},
            ]

        for typ in types:
            for input in inputs:
                msg = typ()
                self.failUnlessRaises(ax.AXError, msg.parseExtensionArgs,
                                      input)

    def test_countPresentAndIsZero(self):
        self.failUnlessAXValues(
            {'type.foo':'urn:foo',
             'count.foo':'0',
             }, {'urn:foo':[]})

    def test_singletonEmpty(self):
        self.failUnlessAXValues(
            {'type.foo':'urn:foo',
             'value.foo':'',
             }, {'urn:foo':[]})

    def test_doubleAlias(self):
        self.failUnlessAXKeyError(
            {'type.foo':'urn:foo',
             'value.foo':'',
             'type.bar':'urn:foo',
             'value.bar':'',
             })

    def test_doubleSingleton(self):
        self.failUnlessAXValues(
            {'type.foo':'urn:foo',
             'value.foo':'',
             'type.bar':'urn:bar',
             'value.bar':'',
             }, {'urn:foo':[], 'urn:bar':[]})

    def test_singletonValue(self):
        self.failUnlessAXValues(
            {'type.foo':'urn:foo',
             'value.foo':'Westfall',
             }, {'urn:foo':['Westfall']})


class FetchRequestTest(unittest.TestCase):
    def setUp(self):
        self.msg = ax.FetchRequest()
        self.type_a = 'http://janrain.example.com/a'
        self.alias_a = 'a'


    def test_mode(self):
        self.failUnlessEqual(self.msg.mode, 'fetch_request')

    def test_construct(self):
        self.failUnlessEqual({}, self.msg.requested_attributes)
        self.failUnlessEqual(None, self.msg.update_url)

        msg = ax.FetchRequest('hailstorm')
        self.failUnlessEqual({}, msg.requested_attributes)
        self.failUnlessEqual('hailstorm', msg.update_url)

    def test_add(self):
        uri = 'mud://puddle'

        # Not yet added:
        self.failIf(uri in self.msg)

        attr = ax.AttrInfo(uri)
        self.msg.add(attr)

        # Present after adding
        self.failUnless(uri in self.msg)

    def test_addTwice(self):
        uri = 'lightning://storm'

        attr = ax.AttrInfo(uri)
        self.msg.add(attr)
        self.failUnlessRaises(KeyError, self.msg.add, attr)

    def test_getExtensionArgs_empty(self):
        expected_args = {
            'mode':'fetch_request',
            }
        self.failUnlessEqual(expected_args, self.msg.getExtensionArgs())

    def test_getExtensionArgs_noAlias(self):
        attr = ax.AttrInfo(
            type_uri = 'type://of.transportation',
            )
        self.msg.add(attr)
        ax_args = self.msg.getExtensionArgs()
        for k, v in ax_args.iteritems():
            if v == attr.type_uri and k.startswith('type.'):
                alias = k[5:]
                break
        else:
            self.fail("Didn't find the type definition")

        self.failUnlessExtensionArgs({
            'type.' + alias:attr.type_uri,
            'if_available':alias,
            })

    def test_getExtensionArgs_alias_if_available(self):
        attr = ax.AttrInfo(
            type_uri = 'type://of.transportation',
            alias = 'transport',
            )
        self.msg.add(attr)
        self.failUnlessExtensionArgs({
            'type.' + attr.alias:attr.type_uri,
            'if_available':attr.alias,
            })

    def test_getExtensionArgs_alias_req(self):
        attr = ax.AttrInfo(
            type_uri = 'type://of.transportation',
            alias = 'transport',
            required = True,
            )
        self.msg.add(attr)
        self.failUnlessExtensionArgs({
            'type.' + attr.alias:attr.type_uri,
            'required':attr.alias,
            })

    def failUnlessExtensionArgs(self, expected_args):
        """Make sure that getExtensionArgs has the expected result

        This method will fill in the mode.
        """
        expected_args = dict(expected_args)
        expected_args['mode'] = self.msg.mode
        self.failUnlessEqual(expected_args, self.msg.getExtensionArgs())

    def test_isIterable(self):
        self.failUnlessEqual([], list(self.msg))
        self.failUnlessEqual([], list(self.msg.iterAttrs()))

    def test_getRequiredAttrs_empty(self):
        self.failUnlessEqual([], self.msg.getRequiredAttrs())

    def test_parseExtensionArgs_extraType(self):
        extension_args = {
            'mode':'fetch_request',
            'type.' + self.alias_a:self.type_a,
            }
        self.failUnlessRaises(ValueError,
                              self.msg.parseExtensionArgs, extension_args)

    def test_parseExtensionArgs(self):
        extension_args = {
            'mode':'fetch_request',
            'type.' + self.alias_a:self.type_a,
            'if_available':self.alias_a
            }
        self.msg.parseExtensionArgs(extension_args)
        self.failUnless(self.type_a in self.msg)
        self.failUnlessEqual([self.type_a], list(self.msg))
        attr_info = self.msg.requested_attributes.get(self.type_a)
        self.failUnless(attr_info)
        self.failIf(attr_info.required)
        self.failUnlessEqual(self.type_a, attr_info.type_uri)
        self.failUnlessEqual(self.alias_a, attr_info.alias)
        self.failUnlessEqual([attr_info], list(self.msg.iterAttrs()))

    def test_extensionArgs_idempotent(self):
        extension_args = {
            'mode':'fetch_request',
            'type.' + self.alias_a:self.type_a,
            'if_available':self.alias_a
            }
        self.msg.parseExtensionArgs(extension_args)
        self.failUnlessEqual(extension_args, self.msg.getExtensionArgs())
        self.failIf(self.msg.requested_attributes[self.type_a].required)

    def test_extensionArgs_idempotent_count_required(self):
        extension_args = {
            'mode':'fetch_request',
            'type.' + self.alias_a:self.type_a,
            'count.' + self.alias_a:'2',
            'required':self.alias_a
            }
        self.msg.parseExtensionArgs(extension_args)
        self.failUnlessEqual(extension_args, self.msg.getExtensionArgs())
        self.failUnless(self.msg.requested_attributes[self.type_a].required)

    def test_extensionArgs_count1(self):
        extension_args = {
            'mode':'fetch_request',
            'type.' + self.alias_a:self.type_a,
            'count.' + self.alias_a:'1',
            'if_available':self.alias_a,
            }
        extension_args_norm = {
            'mode':'fetch_request',
            'type.' + self.alias_a:self.type_a,
            'if_available':self.alias_a,
            }
        self.msg.parseExtensionArgs(extension_args)
        self.failUnlessEqual(extension_args_norm, self.msg.getExtensionArgs())

    def test_openidNoRealm(self):
        openid_req_msg = Message.fromOpenIDArgs({
            'mode': 'checkid_setup',
            'ns': OPENID2_NS,
            'ns.ax': ax.AXMessage.ns_uri,
            'ax.update_url': 'http://different.site/path',
            'ax.mode': 'fetch_request',
            })
        self.failUnlessRaises(ax.AXError,
                              ax.FetchRequest.fromOpenIDRequest,
                              DummyRequest(openid_req_msg))

    def test_openidUpdateURLVerificationError(self):
        openid_req_msg = Message.fromOpenIDArgs({
            'mode': 'checkid_setup',
            'ns': OPENID2_NS,
            'realm': 'http://example.com/realm',
            'ns.ax': ax.AXMessage.ns_uri,
            'ax.update_url': 'http://different.site/path',
            'ax.mode': 'fetch_request',
            })

        self.failUnlessRaises(ax.AXError,
                              ax.FetchRequest.fromOpenIDRequest,
                              DummyRequest(openid_req_msg))

    def test_openidUpdateURLVerificationSuccess(self):
        openid_req_msg = Message.fromOpenIDArgs({
            'mode': 'checkid_setup',
            'ns': OPENID2_NS,
            'realm': 'http://example.com/realm',
            'ns.ax': ax.AXMessage.ns_uri,
            'ax.update_url': 'http://example.com/realm/update_path',
            'ax.mode': 'fetch_request',
            })

        fr = ax.FetchRequest.fromOpenIDRequest(DummyRequest(openid_req_msg))

    def test_openidUpdateURLVerificationSuccessReturnTo(self):
        openid_req_msg = Message.fromOpenIDArgs({
            'mode': 'checkid_setup',
            'ns': OPENID2_NS,
            'return_to': 'http://example.com/realm',
            'ns.ax': ax.AXMessage.ns_uri,
            'ax.update_url': 'http://example.com/realm/update_path',
            'ax.mode': 'fetch_request',
            })

        fr = ax.FetchRequest.fromOpenIDRequest(DummyRequest(openid_req_msg))

    def test_fromOpenIDRequestWithoutExtension(self):
        """return None for an OpenIDRequest without AX paramaters."""
        openid_req_msg = Message.fromOpenIDArgs({
            'mode': 'checkid_setup',
            'ns': OPENID2_NS,
            })
        oreq = DummyRequest(openid_req_msg)
        r = ax.FetchRequest.fromOpenIDRequest(oreq)
        self.failUnless(r is None, "%s is not None" % (r,))

    def test_fromOpenIDRequestWithoutData(self):
        """return something for SuccessResponse with AX paramaters,
        even if it is the empty set."""
        openid_req_msg = Message.fromOpenIDArgs({
            'mode': 'checkid_setup',
            'realm': 'http://example.com/realm',
            'ns': OPENID2_NS,
            'ns.ax': ax.AXMessage.ns_uri,
            'ax.mode': 'fetch_request',
            })
        oreq = DummyRequest(openid_req_msg)
        r = ax.FetchRequest.fromOpenIDRequest(oreq)
        self.failUnless(r is not None)


class FetchResponseTest(unittest.TestCase):
    def setUp(self):
        self.msg = ax.FetchResponse()
        self.value_a = 'monkeys'
        self.type_a = 'http://phone.home/'
        self.alias_a = 'robocop'
        self.request_update_url = 'http://update.bogus/'

    def test_construct(self):
        self.failUnless(self.msg.update_url is None)
        self.failUnlessEqual({}, self.msg.data)

    def test_getExtensionArgs_empty(self):
        expected_args = {
            'mode':'fetch_response',
            }
        self.failUnlessEqual(expected_args, self.msg.getExtensionArgs())

    def test_getExtensionArgs_empty_request(self):
        expected_args = {
            'mode':'fetch_response',
            }
        req = ax.FetchRequest()
        msg = ax.FetchResponse(request=req)
        self.failUnlessEqual(expected_args, msg.getExtensionArgs())

    def test_getExtensionArgs_empty_request_some(self):
        uri = 'http://not.found/'
        alias = 'ext0'

        expected_args = {
            'mode':'fetch_response',
            'type.%s' % (alias,): uri,
            'count.%s' % (alias,): '0'
            }
        req = ax.FetchRequest()
        req.add(ax.AttrInfo(uri))
        msg = ax.FetchResponse(request=req)
        self.failUnlessEqual(expected_args, msg.getExtensionArgs())

    def test_updateUrlInResponse(self):
        uri = 'http://not.found/'
        alias = 'ext0'

        expected_args = {
            'mode':'fetch_response',
            'update_url': self.request_update_url,
            'type.%s' % (alias,): uri,
            'count.%s' % (alias,): '0'
            }
        req = ax.FetchRequest(update_url=self.request_update_url)
        req.add(ax.AttrInfo(uri))
        msg = ax.FetchResponse(request=req)
        self.failUnlessEqual(expected_args, msg.getExtensionArgs())

    def test_getExtensionArgs_some_request(self):
        expected_args = {
            'mode':'fetch_response',
            'type.' + self.alias_a:self.type_a,
            'value.' + self.alias_a + '.1':self.value_a,
            'count.' + self.alias_a: '1'
            }
        req = ax.FetchRequest()
        req.add(ax.AttrInfo(self.type_a, alias=self.alias_a))
        msg = ax.FetchResponse(request=req)
        msg.addValue(self.type_a, self.value_a)
        self.failUnlessEqual(expected_args, msg.getExtensionArgs())

    def test_getExtensionArgs_some_not_request(self):
        req = ax.FetchRequest()
        msg = ax.FetchResponse(request=req)
        msg.addValue(self.type_a, self.value_a)
        self.failUnlessRaises(KeyError, msg.getExtensionArgs)

    def test_getSingle_success(self):
        req = ax.FetchRequest()
        self.msg.addValue(self.type_a, self.value_a)
        self.failUnlessEqual(self.value_a, self.msg.getSingle(self.type_a))

    def test_getSingle_none(self):
        self.failUnlessEqual(None, self.msg.getSingle(self.type_a))

    def test_getSingle_extra(self):
        self.msg.setValues(self.type_a, ['x', 'y'])
        self.failUnlessRaises(ax.AXError, self.msg.getSingle, self.type_a)

    def test_get(self):
        self.failUnlessRaises(KeyError, self.msg.get, self.type_a)

    def test_fromSuccessResponseWithoutExtension(self):
        """return None for SuccessResponse with no AX paramaters."""
        args = {
            'mode': 'id_res',
            'ns': OPENID2_NS,
            }
        sf = ['openid.' + i for i in args.keys()]
        msg = Message.fromOpenIDArgs(args)
        class Endpoint:
            claimed_id = 'http://invalid.'

        oreq = SuccessResponse(Endpoint(), msg, signed_fields=sf)
        r = ax.FetchResponse.fromSuccessResponse(oreq)
        self.failUnless(r is None, "%s is not None" % (r,))

    def test_fromSuccessResponseWithoutData(self):
        """return something for SuccessResponse with AX paramaters,
        even if it is the empty set."""
        args = {
            'mode': 'id_res',
            'ns': OPENID2_NS,
            'ns.ax': ax.AXMessage.ns_uri,
            'ax.mode': 'fetch_response',
            }
        sf = ['openid.' + i for i in args.keys()]
        msg = Message.fromOpenIDArgs(args)
        class Endpoint:
            claimed_id = 'http://invalid.'

        oreq = SuccessResponse(Endpoint(), msg, signed_fields=sf)
        r = ax.FetchResponse.fromSuccessResponse(oreq)
        self.failUnless(r is not None)


class StoreRequestTest(unittest.TestCase):
    def setUp(self):
        self.msg = ax.StoreRequest()
        self.type_a = 'http://three.count/'
        self.alias_a = 'juggling'

    def test_construct(self):
        self.failUnlessEqual({}, self.msg.data)

    def test_getExtensionArgs_empty(self):
        args = self.msg.getExtensionArgs()
        expected_args = {
            'mode':'store_request',
            }
        self.failUnlessEqual(expected_args, args)

    def test_getExtensionArgs_nonempty(self):
        aliases = NamespaceMap()
        aliases.addAlias(self.type_a, self.alias_a)
        msg = ax.StoreRequest(aliases=aliases)
        msg.setValues(self.type_a, ['foo', 'bar'])
        args = msg.getExtensionArgs()
        expected_args = {
            'mode':'store_request',
            'type.' + self.alias_a: self.type_a,
            'count.' + self.alias_a: '2',
            'value.%s.1' % (self.alias_a,):'foo',
            'value.%s.2' % (self.alias_a,):'bar',
            }
        self.failUnlessEqual(expected_args, args)

class StoreResponseTest(unittest.TestCase):
    def test_success(self):
        msg = ax.StoreResponse()
        self.failUnless(msg.succeeded())
        self.failIf(msg.error_message)
        self.failUnlessEqual({'mode':'store_response_success'},
                             msg.getExtensionArgs())

    def test_fail_nomsg(self):
        msg = ax.StoreResponse(False)
        self.failIf(msg.succeeded())
        self.failIf(msg.error_message)
        self.failUnlessEqual({'mode':'store_response_failure'},
                             msg.getExtensionArgs())

    def test_fail_msg(self):
        reason = 'no reason, really'
        msg = ax.StoreResponse(False, reason)
        self.failIf(msg.succeeded())
        self.failUnlessEqual(reason, msg.error_message)
        self.failUnlessEqual({'mode':'store_response_failure',
                              'error':reason}, msg.getExtensionArgs())
