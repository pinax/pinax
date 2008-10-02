import math
from unittest import TestCase

import simplejson as S

class TestFloat(TestCase):
    def test_floats(self):
        for num in [1617161771.7650001, math.pi, math.pi**100, math.pi**-100]:
            self.assertEquals(float(S.dumps(num)), num)
