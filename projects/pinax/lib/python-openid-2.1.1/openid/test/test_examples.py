"Test some examples."

import socket
import os.path, unittest, sys, time
from cStringIO import StringIO

import twill.commands, twill.parse, twill.unit

from openid.consumer.discover import \
     OpenIDServiceEndpoint, OPENID_1_1_TYPE
from openid.consumer.consumer import AuthRequest

class TwillTest(twill.unit.TestInfo):
    """Variant of twill.unit.TestInfo that runs a function as a test script,
    not twill script from a file.
    """

    # twill.unit is pretty small to start with, we're overriding
    # run_script and bypassing twill.parse, so it may make sense to
    # rewrite twill.unit altogether.

    # Desirable features:
    #  * better unittest.TestCase integration.
    #     - handle logs on setup and teardown.
    #     - treat TwillAssertionError as failed test assertion, make twill
    #       assertions more consistant with TestCase.failUnless idioms.
    #     - better error reporting on failed assertions.
    #     - The amount of functions passed back and forth between TestInfo
    #       and TestCase is currently pretty silly.
    #  * access to child process's logs.
    #       TestInfo.start_server redirects stdout/stderr to StringIO
    #       objects which are, afaict, inaccessible to the caller of
    #       test.unit.run_child_process.
    #  * notice when the child process dies, i.e. if you muck up and
    #       your runExampleServer function throws an exception.

    def run_script(self):
        time.sleep(self.sleep)
        # twill.commands.go(self.get_url())
        self.script(self)


def splitDir(d, count):
    # in python2.4 and above, it's easier to spell this as
    # d.rsplit(os.sep, count)
    for i in xrange(count):
        d = os.path.dirname(d)
    return d

def runExampleServer(host, port, data_path):
    thisfile = os.path.abspath(sys.modules[__name__].__file__)
    topDir = splitDir(thisfile, 3)
    exampleDir = os.path.join(topDir, 'examples')
    serverExample = os.path.join(exampleDir, 'server.py')
    serverModule = {}
    execfile(serverExample, serverModule)
    serverMain = serverModule['main']

    serverMain(host, port, data_path)



class TestServer(unittest.TestCase):
    """Acceptance tests for examples/server.py.

    These are more acceptance tests than unit tests as they actually
    start the whole server running and test it on its external HTTP
    interface.
    """

    def setUp(self):
        self.twillOutput = StringIO()
        self.twillErr = StringIO()
        twill.set_output(self.twillOutput)
        twill.set_errout(self.twillErr)
        # FIXME: make sure we pick an available port.
        self.server_port = 8080

        # We need something to feed the server as a realm, but it needn't
        # be reachable.  (Until we test realm verification.)
        self.realm = 'http://127.0.0.1/%s' % (self.id(),)
        self.return_to = self.realm + '/return_to'

        twill.commands.reset_browser()


    def runExampleServer(self):
        """Zero-arg run-the-server function to be passed to TestInfo."""
        # FIXME - make sure sstore starts clean.
        runExampleServer('127.0.0.1', self.server_port, 'sstore')


    def v1endpoint(self, port):
        """Return an OpenID 1.1 OpenIDServiceEndpoint for the server."""
        base = "http://%s:%s" % (socket.getfqdn('127.0.0.1'), port)
        ep = OpenIDServiceEndpoint()
        ep.claimed_id = base + "/id/bob"
        ep.server_url = base + "/openidserver"
        ep.type_uris = [OPENID_1_1_TYPE]
        return ep


    # TODO: test discovery

    def test_checkidv1(self):
        """OpenID 1.1 checkid_setup request."""
        ti = TwillTest(self.twill_checkidv1, self.runExampleServer,
                       self.server_port, sleep=0.2)
        twill.unit.run_test(ti)

        if self.twillErr.getvalue():
            self.fail(self.twillErr.getvalue())


    def test_allowed(self):
        """OpenID 1.1 checkid_setup request."""
        ti = TwillTest(self.twill_allowed, self.runExampleServer,
                       self.server_port, sleep=0.2)
        twill.unit.run_test(ti)

        if self.twillErr.getvalue():
            self.fail(self.twillErr.getvalue())


    def twill_checkidv1(self, twillInfo):
        endpoint = self.v1endpoint(self.server_port)
        authreq = AuthRequest(endpoint, assoc=None)
        url = authreq.redirectURL(self.realm, self.return_to)

        c = twill.commands

        try:
            c.go(url)
            c.get_browser()._browser.set_handle_redirect(False)
            c.submit("yes")
            c.code(302)
            headers = c.get_browser()._browser.response().info()
            finalURL = headers['Location']
            self.failUnless('openid.mode=id_res' in finalURL, finalURL)
            self.failUnless('openid.identity=' in finalURL, finalURL)
        except twill.commands.TwillAssertionError, e:
            msg = '%s\nFinal page:\n%s' % (
                str(e), c.get_browser().get_html())
            self.fail(msg)


    def twill_allowed(self, twillInfo):
        endpoint = self.v1endpoint(self.server_port)
        authreq = AuthRequest(endpoint, assoc=None)
        url = authreq.redirectURL(self.realm, self.return_to)

        c = twill.commands

        try:
            c.go(url)
            c.code(200)
            c.get_browser()._browser.set_handle_redirect(False)
            c.formvalue(1, 'remember', 'true')
            c.find('name="login_as" value="bob"')
            c.submit("yes")
            c.code(302)
            # Since we set remember=yes, the second time we shouldn't
            # see that page.
            c.go(url)
            c.code(302)
            headers = c.get_browser()._browser.response().info()
            finalURL = headers['Location']
            self.failUnless(finalURL.startswith(self.return_to))
        except twill.commands.TwillAssertionError, e:
            from traceback import format_exc
            msg = '%s\nTwill output:%s\nTwill errors:%s\nFinal page:\n%s' % (
                format_exc(),
                self.twillOutput.getvalue(),
                self.twillErr.getvalue(),
                c.get_browser().get_html())
            self.fail(msg)


    def tearDown(self):
        twill.set_output(None)
        twill.set_errout(None)


if __name__ == '__main__':
    unittest.main()
