from unittest import TestCase

import simplejson as S

class TestDefault(TestCase):
    def test_default(self):
        self.assertEquals(
            S.dumps(type, default=repr),
            S.dumps(repr(type)))
