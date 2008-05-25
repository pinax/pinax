import unittest
import codecs
import string
import random
from openid import oidutil

def test_base64():
    allowed_s = string.ascii_letters + string.digits + '+/='
    allowed_d = {}
    for c in allowed_s:
        allowed_d[c] = None
    isAllowed = allowed_d.has_key

    def checkEncoded(s):
        for c in s:
            assert isAllowed(c), s

    cases = [
        '',
        'x',
        '\x00',
        '\x01',
        '\x00' * 100,
        ''.join(map(chr, range(256))),
        ]

    for s in cases:
        b64 = oidutil.toBase64(s)
        checkEncoded(b64)
        s_prime = oidutil.fromBase64(b64)
        assert s_prime == s, (s, b64, s_prime)

    # Randomized test
    for _ in xrange(50):
        n = random.randrange(2048)
        s = ''.join(map(chr, map(lambda _: random.randrange(256), range(n))))
        b64 = oidutil.toBase64(s)
        checkEncoded(b64)
        s_prime = oidutil.fromBase64(b64)
        assert s_prime == s, (s, b64, s_prime)

class AppendArgsTest(unittest.TestCase):
    def __init__(self, desc, args, expected):
        unittest.TestCase.__init__(self)
        self.desc = desc
        self.args = args
        self.expected = expected

    def runTest(self):
        result = oidutil.appendArgs(*self.args)
        self.assertEqual(self.expected, result, self.args)

    def shortDescription(self):
        return self.desc



class TestSymbol(unittest.TestCase):
    def testCopyHash(self):
        import copy
        s = oidutil.Symbol("Foo")
        d = {s: 1}
        d_prime = copy.deepcopy(d)
        self.failUnless(s in d_prime, "%r isn't in %r" % (s, d_prime))

        t = oidutil.Symbol("Bar")
        self.failIfEqual(hash(s), hash(t))


def buildAppendTests():
    simple = 'http://www.example.com/'
    cases = [
        ('empty list',
         (simple, []),
         simple),

        ('empty dict',
         (simple, {}),
         simple),

        ('one list',
         (simple, [('a', 'b')]),
         simple + '?a=b'),

        ('one dict',
         (simple, {'a':'b'}),
         simple + '?a=b'),

        ('two list (same)',
         (simple, [('a', 'b'), ('a', 'c')]),
         simple + '?a=b&a=c'),

        ('two list',
         (simple, [('a', 'b'), ('b', 'c')]),
         simple + '?a=b&b=c'),

        ('two list (order)',
         (simple, [('b', 'c'), ('a', 'b')]),
         simple + '?b=c&a=b'),

        ('two dict (order)',
         (simple, {'b':'c', 'a':'b'}),
         simple + '?a=b&b=c'),

        ('escape',
         (simple, [('=', '=')]),
         simple + '?%3D=%3D'),

        ('escape (URL)',
         (simple, [('this_url', simple)]),
         simple + '?this_url=http%3A%2F%2Fwww.example.com%2F'),

        ('use dots',
         (simple, [('openid.stuff', 'bother')]),
         simple + '?openid.stuff=bother'),

        ('args exist (empty)',
         (simple + '?stuff=bother', []),
         simple + '?stuff=bother'),

        ('args exist',
         (simple + '?stuff=bother', [('ack', 'ack')]),
         simple + '?stuff=bother&ack=ack'),

        ('args exist',
         (simple + '?stuff=bother', [('ack', 'ack')]),
         simple + '?stuff=bother&ack=ack'),

        ('args exist (dict)',
         (simple + '?stuff=bother', {'ack': 'ack'}),
         simple + '?stuff=bother&ack=ack'),

        ('args exist (dict 2)',
         (simple + '?stuff=bother', {'ack': 'ack', 'zebra':'lion'}),
         simple + '?stuff=bother&ack=ack&zebra=lion'),

        ('three args (dict)',
         (simple, {'stuff': 'bother', 'ack': 'ack', 'zebra':'lion'}),
         simple + '?ack=ack&stuff=bother&zebra=lion'),

        ('three args (list)',
         (simple, [('stuff', 'bother'), ('ack', 'ack'), ('zebra', 'lion')]),
         simple + '?stuff=bother&ack=ack&zebra=lion'),
        ]

    tests = []

    for name, args, expected in cases:
        test = AppendArgsTest(name, args, expected)
        tests.append(test)

    return unittest.TestSuite(tests)

def pyUnitTests():
    some = buildAppendTests()
    some.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestSymbol))
    return some

def test_appendArgs():
    suite = buildAppendTests()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestSymbol))
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    assert result.wasSuccessful()

# XXX: there are more functions that could benefit from being better
# specified and tested in oidutil.py These include, but are not
# limited to appendArgs

def test(skipPyUnit=True):
    test_base64()
    if not skipPyUnit:
        test_appendArgs()

if __name__ == '__main__':
    test(skipPyUnit=False)
