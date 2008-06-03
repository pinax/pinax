from openid.consumer.discover import OpenIDServiceEndpoint
import datadriven

class BadLinksTestCase(datadriven.DataDrivenTestCase):
    cases = [
        '',
        "http://not.in.a.link.tag/",
        '<link rel="openid.server" href="not.in.html.or.head" />',
        ]

    def __init__(self, data):
        datadriven.DataDrivenTestCase.__init__(self, data)
        self.data = data

    def runOneTest(self):
        actual = OpenIDServiceEndpoint.fromHTML('http://unused.url/', self.data)
        expected = []
        self.failUnlessEqual(expected, actual)

def pyUnitTests():
    return datadriven.loadTests(__name__)
