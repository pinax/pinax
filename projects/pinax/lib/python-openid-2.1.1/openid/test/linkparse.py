from openid.consumer.html_parse import parseLinkAttrs
import os.path
import codecs
import unittest

def parseLink(line):
    parts = line.split()
    optional = parts[0] == 'Link*:'
    assert optional or parts[0] == 'Link:'

    attrs = {}
    for attr in parts[1:]:
        k, v = attr.split('=', 1)
        if k[-1] == '*':
            attr_optional = 1
            k = k[:-1]
        else:
            attr_optional = 0

        attrs[k] = (attr_optional, v)

    return (optional, attrs)

def parseCase(s):
    header, markup = s.split('\n\n', 1)
    lines = header.split('\n')
    name = lines.pop(0)
    assert name.startswith('Name: ')
    desc = name[6:]
    return desc, markup, map(parseLink, lines)

def parseTests(s):
    tests = []

    cases = s.split('\n\n\n')
    header = cases.pop(0)
    tests_line, _ = header.split('\n', 1)
    k, v = tests_line.split(': ')
    assert k == 'Num Tests'
    num_tests = int(v)

    for case in cases[:-1]:
        desc, markup, links = parseCase(case)
        tests.append((desc, markup, links, case))

    return num_tests, tests

class _LinkTest(unittest.TestCase):
    def __init__(self, desc, case, expected, raw):
        unittest.TestCase.__init__(self)
        self.desc = desc
        self.case = case
        self.expected = expected
        self.raw = raw

    def shortDescription(self):
        return self.desc

    def runTest(self):
        actual = parseLinkAttrs(self.case)
        i = 0
        for optional, exp_link in self.expected:
            if optional:
                if i >= len(actual):
                    continue

            act_link = actual[i]
            for k, (o, v) in exp_link.items():
                if o:
                    act_v = act_link.get(k)
                    if act_v is None:
                        continue
                else:
                    act_v = act_link[k]

                if optional and v != act_v:
                    break

                self.assertEqual(v, act_v)
            else:
                i += 1

        assert i == len(actual)

def pyUnitTests():
    here = os.path.dirname(os.path.abspath(__file__))
    test_data_file_name = os.path.join(here, 'linkparse.txt')
    test_data_file = codecs.open(test_data_file_name, 'r', 'utf-8')
    test_data = test_data_file.read()
    test_data_file.close()

    num_tests, test_cases = parseTests(test_data)

    tests = [_LinkTest(*case) for case in test_cases]

    def test_parseSucceeded():
        assert len(test_cases) == num_tests, (len(test_cases), num_tests)

    check_desc = 'Check that we parsed the correct number of test cases'
    check = unittest.FunctionTestCase(
        test_parseSucceeded, description=check_desc)
    tests.insert(0, check)

    return unittest.TestSuite(tests)

if __name__ == '__main__':
    suite = pyUnitTests()
    runner = unittest.TextTestRunner()
    runner.run(suite)
