from unittest import TestCase
from cStringIO import StringIO

import simplejson as S

class TestDump(TestCase):
    def test_dump(self):
        sio = StringIO()
        S.dump({}, sio)
        self.assertEquals(sio.getvalue(), '{}')
    
    def test_dumps(self):
        self.assertEquals(S.dumps({}), '{}')
