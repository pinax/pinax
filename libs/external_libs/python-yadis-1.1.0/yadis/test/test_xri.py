
from unittest import TestCase
from yadis import xri

class XriDiscoveryTestCase(TestCase):
    def test_isXRI(self):
        i = xri.identifierScheme
        self.failUnlessEqual(i('=john.smith'), 'XRI')
        self.failUnlessEqual(i('@smiths/john'), 'XRI')
        self.failUnlessEqual(i('smoker.myopenid.com'), 'URI')
        self.failUnlessEqual(i('xri://=john'), 'XRI')


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
    providerIsAuthoritativeCases = [
        # provider, canonicalID, isAuthoritative
        ('=', '=!698.74D1.A1F2.86C7', True),
        ('@!1234', '@!1234!ABCD', True),
        ('@!1234!5678', '@!1234!5678!ABCD', True),
        ('@!1234', '=!1234!ABCD', False),
        ('@!1234', '@!1234!ABCD!9765', False),
        ('@!1234!ABCD', '=!1234', False),
        ('=!BABE', '=!D00D', False),
        ]


    def test_providerIsAuthoritative(self):
        """Checking whether this provider is authoratitve for
        the given XRI."""
        # XXX: Should perhaps be more like the other data-driven tests?
        for providerID, canonicalID, isAuthoritative in \
                self.providerIsAuthoritativeCases:
            self._providerIsAuthoritative(providerID, canonicalID,
                                          isAuthoritative)


    def _providerIsAuthoritative(self, providerID, canonicalID, expected):
        result = xri.providerIsAuthoritative(providerID, canonicalID)
        self.failUnlessEqual(expected, result,
                             "%s providing %s, expected %s" % (providerID,
                                                               canonicalID,
                                                               expected))



class TestGetRootAuthority(TestCase):
    xris = [
        ("@foo", "@"),
        ("@foo*bar", "@"),
        ("@*foo*bar", "@"),
        ("@foo/bar", "@"),
        ("!!990!991", "!"),
        ("!1001!02", "!"),
        ("=foo*bar", "="),
        ("(example.com)/foo", "(example.com)"),
        ("(example.com)*bar/foo", "(example.com)"),
        ("baz.example.com/foo", "baz.example.com"),
        ("baz.example.com:8080/foo", "baz.example.com:8080"),
        # Looking at the ABNF in XRI Syntax 2.0, I don't think you can
        # have example.com*bar.  You can do (example.com)*bar, but that
        # would mean something else.
        ##("example.com*bar/(=baz)", "example.com*bar"),
        ##("baz.example.com!01/foo", "baz.example.com!01"),
        ]


    def test_getRootAuthority(self):
        for thexri, expected_root in self.xris:
            self.failUnlessEqual(xri.rootAuthority(thexri),
                                 xri.XRI(expected_root))



if __name__ == '__main__':
    import unittest
    unittest.main()
