import sys
import random
import os.path

from openid import cryptutil

# Most of the purpose of this test is to make sure that cryptutil can
# find a good source of randomness on this machine.

def test_cryptrand():
    # It's possible, but HIGHLY unlikely that a correct implementation
    # will fail by returning the same number twice

    s = cryptutil.getBytes(32)
    t = cryptutil.getBytes(32)
    assert len(s) == 32
    assert len(t) == 32
    assert s != t

    a = cryptutil.randrange(2L ** 128)
    b = cryptutil.randrange(2L ** 128)
    assert type(a) is long
    assert type(b) is long
    assert b != a

    # Make sure that we can generate random numbers that are larger
    # than platform int size
    cryptutil.randrange(long(sys.maxint) + 1L)

def test_reversed():
    if hasattr(cryptutil, 'reversed'):
        cases = [
            ('', ''),
            ('a', 'a'),
            ('ab', 'ba'),
            ('abc', 'cba'),
            ('abcdefg', 'gfedcba'),
            ([], []),
            ([1], [1]),
            ([1,2], [2,1]),
            ([1,2,3], [3,2,1]),
            (range(1000), range(999, -1, -1)),
            ]

        for case, expected in cases:
            expected = list(expected)
            actual = list(cryptutil.reversed(case))
            assert actual == expected, (case, expected, actual)
            twice = list(cryptutil.reversed(actual))
            assert twice == list(case), (actual, case, twice)

def test_binaryLongConvert():
    MAX = sys.maxint
    for iteration in xrange(500):
        n = 0L
        for i in range(10):
            n += long(random.randrange(MAX))

        s = cryptutil.longToBinary(n)
        assert type(s) is str
        n_prime = cryptutil.binaryToLong(s)
        assert n == n_prime, (n, n_prime)

    cases = [
        ('\x00', 0L),
        ('\x01', 1L),
        ('\x7F', 127L),
        ('\x00\xFF', 255L),
        ('\x00\x80', 128L),
        ('\x00\x81', 129L),
        ('\x00\x80\x00', 32768L),
        ('OpenID is cool', 1611215304203901150134421257416556L)
        ]

    for s, n in cases:
        n_prime = cryptutil.binaryToLong(s)
        s_prime = cryptutil.longToBinary(n)
        assert n == n_prime, (s, n, n_prime)
        assert s == s_prime, (n, s, s_prime)

def test_longToBase64():
    f = file(os.path.join(os.path.dirname(__file__), 'n2b64'))
    try:
        for line in f:
            parts = line.strip().split(' ')
            assert parts[0] == cryptutil.longToBase64(long(parts[1]))
    finally:
        f.close()

def test_base64ToLong():
    f = file(os.path.join(os.path.dirname(__file__), 'n2b64'))
    try:
        for line in f:
            parts = line.strip().split(' ')
            assert long(parts[1]) == cryptutil.base64ToLong(parts[0])
    finally:
        f.close()


def test():
    test_reversed()
    test_binaryLongConvert()
    test_cryptrand()
    test_longToBase64()
    test_base64ToLong()

if __name__ == '__main__':
    test()
