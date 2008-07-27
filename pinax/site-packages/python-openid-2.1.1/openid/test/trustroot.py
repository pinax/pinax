import os
import unittest
from openid.server.trustroot import TrustRoot

class _ParseTest(unittest.TestCase):
    def __init__(self, sanity, desc, case):
        unittest.TestCase.__init__(self)
        self.desc = desc + ': ' + repr(case)
        self.case = case
        self.sanity = sanity

    def shortDescription(self):
        return self.desc

    def runTest(self):
        tr = TrustRoot.parse(self.case)
        if self.sanity == 'sane':
            assert tr.isSane(), self.case
        elif self.sanity == 'insane':
            assert not tr.isSane(), self.case
        else:
            assert tr is None

class _MatchTest(unittest.TestCase):
    def __init__(self, match, desc, line):
        unittest.TestCase.__init__(self)
        tr, rt = line.split()
        self.desc = desc + ': ' + repr(tr) + ' ' + repr(rt)
        self.tr = tr
        self.rt = rt
        self.match = match

    def shortDescription(self):
        return self.desc

    def runTest(self):
        tr = TrustRoot.parse(self.tr)
        match = tr.validateURL(self.rt)
        if self.match:
            assert match
        else:
            assert not match

def getTests(t, grps, head, dat):
    tests = []
    top = head.strip()
    gdat = map(str.strip, dat.split('-' * 40 + '\n'))
    assert not gdat[0]
    assert len(gdat) == (len(grps) * 2 + 1), (gdat, grps)
    i = 1
    for x in grps:
        n, desc = gdat[i].split(': ')
        cases = gdat[i + 1].split('\n')
        assert len(cases) == int(n)
        for case in cases:
            tests.append(t(x, top + ' - ' + desc, case))
        i += 2
    return tests

def parseTests(data):
    parts = map(str.strip, data.split('=' * 40 + '\n'))
    assert not parts[0]
    _, ph, pdat, mh, mdat = parts

    tests = []
    tests.extend(getTests(_ParseTest, ['bad', 'insane', 'sane'], ph, pdat))
    tests.extend(getTests(_MatchTest, [1, 0], mh, mdat))
    return tests

def pyUnitTests():
    here = os.path.dirname(os.path.abspath(__file__))
    test_data_file_name = os.path.join(here, 'trustroot.txt')
    test_data_file = file(test_data_file_name)
    test_data = test_data_file.read()
    test_data_file.close()

    tests = parseTests(test_data)
    return unittest.TestSuite(tests)

if __name__ == '__main__':
    suite = pyUnitTests()
    runner = unittest.TextTestRunner()
    runner.run(suite)
