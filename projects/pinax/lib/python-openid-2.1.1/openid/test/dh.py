import os.path
from openid.dh import DiffieHellman, strxor

def test_strxor():
    NUL = '\x00'

    cases = [
        (NUL, NUL, NUL),
        ('\x01', NUL, '\x01'),
        ('a', 'a', NUL),
        ('a', NUL, 'a'),
        ('abc', NUL * 3, 'abc'),
        ('x' * 10, NUL * 10, 'x' * 10),
        ('\x01', '\x02', '\x03'),
        ('\xf0', '\x0f', '\xff'),
        ('\xff', '\x0f', '\xf0'),
        ]

    for aa, bb, expected in cases:
        actual = strxor(aa, bb)
        assert actual == expected, (aa, bb, expected, actual)

    exc_cases = [
        ('', 'a'),
        ('foo', 'ba'),
        (NUL * 3, NUL * 4),
        (''.join(map(chr, xrange(256))),
         ''.join(map(chr, xrange(128)))),
        ]

    for aa, bb in exc_cases:
        try:
            unexpected = strxor(aa, bb)
        except ValueError:
            pass
        else:
            assert False, 'Expected ValueError, got %r' % (unexpected,)

def test1():
    dh1 = DiffieHellman.fromDefaults()
    dh2 = DiffieHellman.fromDefaults()
    secret1 = dh1.getSharedSecret(dh2.public)
    secret2 = dh2.getSharedSecret(dh1.public)
    assert secret1 == secret2
    return secret1

def test_exchange():
    s1 = test1()
    s2 = test1()
    assert s1 != s2

def test_public():
    f = file(os.path.join(os.path.dirname(__file__), 'dhpriv'))
    dh = DiffieHellman.fromDefaults()
    try:
        for line in f:
            parts = line.strip().split(' ')
            dh._setPrivate(long(parts[0]))

            assert dh.public == long(parts[1])
    finally:
        f.close()

def test():
    test_exchange()
    test_public()
    test_strxor()

if __name__ == '__main__':
    test()
