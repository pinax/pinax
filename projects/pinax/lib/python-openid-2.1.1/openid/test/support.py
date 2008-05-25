from openid import message
from openid import oidutil

class OpenIDTestMixin(object):
    def failUnlessOpenIDValueEquals(self, msg, key, expected, ns=None):
        if ns is None:
            ns = message.OPENID_NS

        actual = msg.getArg(ns, key)
        error_format = 'Wrong value for openid.%s: expected=%s, actual=%s'
        error_message = error_format % (key, expected, actual)
        self.failUnlessEqual(expected, actual, error_message)

    def failIfOpenIDKeyExists(self, msg, key, ns=None):
        if ns is None:
            ns = message.OPENID_NS

        actual = msg.getArg(ns, key)
        error_message = 'openid.%s unexpectedly present: %s' % (key, actual)
        self.failIf(actual is not None, error_message)

class CatchLogs(object):
    def setUp(self):
        self.old_logger = oidutil.log
        oidutil.log = self.gotLogMessage
        self.messages = []

    def gotLogMessage(self, message):
        self.messages.append(message)

    def tearDown(self):
        oidutil.log = self.old_logger

    def failUnlessLogMatches(self, *prefixes):
        """
        Check that the log messages contained in self.messages have
        prefixes in *prefixes.  Raise AssertionError if not, or if the
        number of prefixes is different than the number of log
        messages.
        """
        assert len(prefixes) == len(self.messages), \
               "Expected log prefixes %r, got %r" % (prefixes,
                                                     self.messages)

        for prefix, message in zip(prefixes, self.messages):
            assert message.startswith(prefix), \
                   "Expected log prefixes %r, got %r" % (prefixes,
                                                         self.messages)

    def failUnlessLogEmpty(self):
        self.failUnlessLogMatches()
