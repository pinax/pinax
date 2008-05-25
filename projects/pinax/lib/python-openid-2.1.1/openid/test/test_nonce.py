from openid.test import datadriven
import time
import unittest
import re

from openid.store.nonce import \
     mkNonce, \
     split as splitNonce, \
     checkTimestamp

nonce_re = re.compile(r'\A\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ')

class NonceTest(unittest.TestCase):
    def test_mkNonce(self):
        nonce = mkNonce()
        self.failUnless(nonce_re.match(nonce))
        self.failUnless(len(nonce) == 26)

    def test_mkNonce_when(self):
        nonce = mkNonce(0)
        self.failUnless(nonce_re.match(nonce))
        self.failUnless(nonce.startswith('1970-01-01T00:00:00Z'))
        self.failUnless(len(nonce) == 26)

    def test_splitNonce(self):
        s = '1970-01-01T00:00:00Z'
        expected_t = 0
        expected_salt = ''
        actual_t, actual_salt = splitNonce(s)
        self.failUnlessEqual(expected_t, actual_t)
        self.failUnlessEqual(expected_salt, actual_salt)

    def test_mkSplit(self):
        t = 42
        nonce_str = mkNonce(t)
        self.failUnless(nonce_re.match(nonce_str))
        et, salt = splitNonce(nonce_str)
        self.failUnlessEqual(len(salt), 6)
        self.failUnlessEqual(et, t)

class BadSplitTest(datadriven.DataDrivenTestCase):
    cases = [
        '',
        '1970-01-01T00:00:00+1:00',
        '1969-01-01T00:00:00Z',
        '1970-00-01T00:00:00Z',
        '1970.01-01T00:00:00Z',
        'Thu Sep  7 13:29:31 PDT 2006',
        'monkeys',
        ]

    def __init__(self, nonce_str):
        datadriven.DataDrivenTestCase.__init__(self, nonce_str)
        self.nonce_str = nonce_str

    def runOneTest(self):
        self.failUnlessRaises(ValueError, splitNonce, self.nonce_str)

class CheckTimestampTest(datadriven.DataDrivenTestCase):
    cases = [
        # exact, no allowed skew
        ('1970-01-01T00:00:00Z', 0, 0, True),

        # exact, large skew
        ('1970-01-01T00:00:00Z', 1000, 0, True),

        # no allowed skew, one second old
        ('1970-01-01T00:00:00Z', 0, 1, False),

        # many seconds old, outside of skew
        ('1970-01-01T00:00:00Z', 10, 50, False),

        # one second old, one second skew allowed
        ('1970-01-01T00:00:00Z', 1, 1, True),

        # One second in the future, one second skew allowed
        ('1970-01-01T00:00:02Z', 1, 1, True),

        # two seconds in the future, one second skew allowed
        ('1970-01-01T00:00:02Z', 1, 0, False),

        # malformed nonce string
        ('monkeys', 0, 0, False),
        ]

    def __init__(self, nonce_string, allowed_skew, now, expected):
        datadriven.DataDrivenTestCase.__init__(
            self, repr((nonce_string, allowed_skew, now)))
        self.nonce_string = nonce_string
        self.allowed_skew = allowed_skew
        self.now = now
        self.expected = expected

    def runOneTest(self):
        actual = checkTimestamp(self.nonce_string, self.allowed_skew, self.now)
        self.failUnlessEqual(bool(self.expected), bool(actual))

def pyUnitTests():
    return datadriven.loadTests(__name__)

if __name__ == '__main__':
    suite = pyUnitTests()
    runner = unittest.TextTestRunner()
    runner.run(suite)
