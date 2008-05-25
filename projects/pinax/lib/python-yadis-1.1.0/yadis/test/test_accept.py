import unittest
import os.path
from yadis import accept

def getTestData():
    """Read the test data off of disk

    () -> [(int, str)]
    """
    filename = os.path.join(os.path.dirname(__file__), 'data', 'accept.txt')
    i = 1
    lines = []
    for line in file(filename):
        lines.append((i, line))
        i += 1
    return lines

def chunk(lines):
    """Return groups of lines separated by whitespace or comments

    [(int, str)] -> [[(int, str)]]
    """
    chunks = []
    chunk = []
    for lineno, line in lines:
        stripped = line.strip()
        if not stripped or stripped[0] == '#':
            if chunk:
                chunks.append(chunk)
                chunk = []
        else:
            chunk.append((lineno, stripped))

    if chunk:
        chunks.append(chunk)

    return chunks

def parseLines(chunk):
    """Take the given chunk of lines and turn it into a test data dictionary

    [(int, str)] -> {str:(int, str)}
    """
    items = {}
    for (lineno, line) in chunk:
        header, data = line.split(':', 1)
        header = header.lower()
        items[header] = (lineno, data.strip())

    return items

def parseAvailable(available_text):
    """Parse an Available: line's data

    str -> [str]
    """
    return [s.strip() for s in available_text.split(',')]

def parseExpected(expected_text):
    """Parse an Expected: line's data

    str -> [(str, float)]
    """
    expected = []
    if expected_text:
        for chunk in expected_text.split(','):
            chunk = chunk.strip()
            mtype, qstuff = chunk.split(';')
            mtype = mtype.strip()
            assert '/' in mtype
            qstuff = qstuff.strip()
            q, qstr = qstuff.split('=')
            assert q == 'q'
            qval = float(qstr)
            expected.append((mtype, qval))

    return expected

class MatchAcceptTest(unittest.TestCase):
    def __init__(self, descr, accept_header, available, expected):
        unittest.TestCase.__init__(self)
        self.accept_header = accept_header
        self.available = available
        self.expected = expected
        self.descr = descr

    def shortDescription(self):
        return self.descr

    def runTest(self):
        accepted = accept.parseAcceptHeader(self.accept_header)
        actual = accept.matchTypes(accepted, self.available)
        self.failUnlessEqual(self.expected, actual)

def loadTests():
    lines = getTestData()
    chunks = chunk(lines)
    data_sets = map(parseLines, chunks)
    cases = []
    for data in data_sets:
        lnos = []
        lno, header = data['accept']
        lnos.append(lno)
        lno, avail_data = data['available']
        lnos.append(lno)
        try:
            available = parseAvailable(avail_data)
        except:
            print 'On line', lno
            raise

        lno, exp_data = data['expected']
        lnos.append(lno)
        try:
            expected = parseExpected(exp_data)
        except:
            print 'On line', lno
            raise

        descr = 'MatchAcceptTest for lines %r' % (lnos,)
        case = MatchAcceptTest(descr, header, available, expected)
        cases.append(case)
    return unittest.TestSuite(cases)

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(loadTests())
