from unittest import TestCase
from openid.yadis import xri

class XriDiscoveryTestCase(TestCase):
    def test_isXRI(self):
        i = xri.identifierScheme
        self.failUnlessEqual(i('=john.smith'), 'XRI')
        self.failUnlessEqual(i('@smiths/john'), 'XRI')
        self.failUnlessEqual(i('smoker.myopenid.com'), 'URI')
        self.failUnlessEqual(i('xri://=john'), 'XRI')
        self.failUnlessEqual(i(''), 'URI')


class XriEscapingTestCase(TestCase):
    def test_escaping_percents(self):
        self.failUnlessEqual(xri.escapeForIRI('@example/abc%2Fd/ef'),
                             '@example/abc%252Fd/ef')


    def test_escaping_xref(self):
        # no escapes
        esc = xri.escapeForIRI
        self.failUnlessEqual('@example/foo/(@bar)', esc('@example/foo/(@bar)'))
        # escape slashes
        self.failUnlessEqual('@example/foo/(@bar%2Fbaz)',
                             esc('@example/foo/(@bar/baz)'))
        self.failUnlessEqual('@example/foo/(@bar%2Fbaz)/(+a%2Fb)',
                             esc('@example/foo/(@bar/baz)/(+a/b)'))
        # escape query ? and fragment #
        self.failUnlessEqual('@example/foo/(@baz%3Fp=q%23r)?i=j#k',
                             esc('@example/foo/(@baz?p=q#r)?i=j#k'))



class XriTransformationTestCase(TestCase):
    def test_to_iri_normal(self):
        self.failUnlessEqual(xri.toIRINormal('@example'), 'xri://@example')

    try:
        unichr(0x10000)
    except ValueError:
        # bleh narrow python build
        def test_iri_to_url(self):
            s = u'l\xa1m'
            expected = 'l%C2%A1m'
            self.failUnlessEqual(xri.iriToURI(s), expected)
    else:
        def test_iri_to_url(self):
            s = u'l\xa1m\U00101010n'
            expected = 'l%C2%A1m%F4%81%80%90n'
            self.failUnlessEqual(xri.iriToURI(s), expected)



class CanonicalIDTest(TestCase):
    def mkTest(providerID, canonicalID, isAuthoritative):
        def test(self):
            result = xri.providerIsAuthoritative(providerID, canonicalID)
            format = "%s providing %s, expected %s"
            message = format % (providerID, canonicalID, isAuthoritative)
            self.failUnlessEqual(isAuthoritative, result, message)

        return test

    test_equals = mkTest('=', '=!698.74D1.A1F2.86C7', True)
    test_atOne = mkTest('@!1234', '@!1234!ABCD', True)
    test_atTwo = mkTest('@!1234!5678', '@!1234!5678!ABCD', True)

    test_atEqualsFails = mkTest('@!1234', '=!1234!ABCD', False)
    test_tooDeepFails = mkTest('@!1234', '@!1234!ABCD!9765', False)
    test_atEqualsAndTooDeepFails = mkTest('@!1234!ABCD', '=!1234', False)
    test_differentBeginningFails = mkTest('=!BABE', '=!D00D', False)

class TestGetRootAuthority(TestCase):
    def mkTest(the_xri, expected_root):
        def test(self):
            actual_root = xri.rootAuthority(the_xri)
            self.failUnlessEqual(actual_root, xri.XRI(expected_root))
        return test

    test_at = mkTest("@foo", "@")
    test_atStar = mkTest("@foo*bar", "@")
    test_atStarStar = mkTest("@*foo*bar", "@")
    test_atWithPath = mkTest("@foo/bar", "@")
    test_bangBang = mkTest("!!990!991", "!")
    test_bang = mkTest("!1001!02", "!")
    test_equalsStar = mkTest("=foo*bar", "=")
    test_xrefPath = mkTest("(example.com)/foo", "(example.com)")
    test_xrefStar = mkTest("(example.com)*bar/foo", "(example.com)")
    test_uriAuth = mkTest("baz.example.com/foo", "baz.example.com")
    test_uriAuthPort = mkTest("baz.example.com:8080/foo",
                              "baz.example.com:8080")

    # Looking at the ABNF in XRI Syntax 2.0, I don't think you can
    # have example.com*bar.  You can do (example.com)*bar, but that
    # would mean something else.
    ##("example.com*bar/(=baz)", "example.com*bar"),
    ##("baz.example.com!01/foo", "baz.example.com!01"),

if __name__ == '__main__':
    import unittest
    unittest.main()
