from openid.yadis.parsehtml import YadisHTMLParser, ParseDone
from HTMLParser import HTMLParseError

import os.path, unittest, sys

class _TestCase(unittest.TestCase):
    reserved_values = ['None', 'EOF']

    def __init__(self, filename, testname, expected, case):
        self.filename = filename
        self.testname = testname
        self.expected = expected
        self.case = case
        unittest.TestCase.__init__(self)

    def runTest(self):
        p = YadisHTMLParser()
        try:
            p.feed(self.case)
        except ParseDone, why:
            found = why[0]

            # make sure we protect outselves against accidental bogus
            # test cases
            assert found not in self.reserved_values

            # convert to a string
            if found is None:
                found = 'None'

            msg = "%r != %r for case %s" % (found, self.expected, self.case)
            self.failUnlessEqual(found, self.expected, msg)
        except HTMLParseError:
            assert self.expected == 'None'
        else:
            self.failUnless(self.expected == 'EOF', (self.case, self.expected))

    def shortDescription(self):
        return "%s (%s<%s>)" % (
            self.testname,
            self.__class__.__module__,
            os.path.basename(self.filename))

def parseCases(data):
    cases = []
    for chunk in data.split('\f\n'):
        expected, case = chunk.split('\n', 1)
        cases.append((expected, case))
    return cases

def pyUnitTests():
    """Make a pyunit TestSuite from a file defining test cases."""
    s = unittest.TestSuite()
    for (filename, test_num, expected, case) in getCases():
        s.addTest(_TestCase(filename, str(test_num), expected, case))
    return s

def test():
    runner = unittest.TextTestRunner()
    return runner.run(loadTests())

filenames = ['data/test1-parsehtml.txt']

default_test_files = []
base = os.path.dirname(__file__)
for filename in filenames:
    full_name = os.path.join(base, filename)
    default_test_files.append(full_name)

def getCases(test_files=default_test_files):
    cases = []
    for filename in test_files:
        test_num = 0
        data = file(filename).read()
        for expected, case in parseCases(data):
            test_num += 1
            cases.append((filename, test_num, expected, case))
    return cases


if __name__ == '__main__':
    sys.exit(not test().wasSuccessful())
