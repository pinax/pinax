import unittest
from pygments.lexer import using, bygroups, this, RegexLexer
from pygments.token import String, Text, Keyword

class TestLexer(RegexLexer):
    tokens = {
        'root': [
            (r'#.*', using(this, state='invalid')),
            (r'(")(.+?)(")', bygroups(String, using(this, state='string'), String)),
            (r'[^"]+', Text),
        ],
        'string': [
            (r'.+', Keyword),
        ],
    }

class UsingStateTest(unittest.TestCase):
    def test_basic(self):
        expected = [(Text, 'a'), (String, '"'), (Keyword, 'bcd'),
                    (String, '"'), (Text, 'e\n')]
        t = list(TestLexer().get_tokens('a"bcd"e'))
        self.assertEquals(t, expected)
    def test_error(self):
        def gen():
            x = list(TestLexer().get_tokens('#a'))
        #XXX: should probably raise a more specific exception if the state
        #     doesn't exist.
        self.assertRaises(Exception, gen)

if __name__ == "__main__":
    unittest.main()
