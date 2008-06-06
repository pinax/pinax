#!/usr/bin/env python2.4
from pkg_resources import require
require('simplejson')

import profile

from simplejson.tests.test_pass1 import test_parse

profile.run("for x in xrange(10): test_parse()")
