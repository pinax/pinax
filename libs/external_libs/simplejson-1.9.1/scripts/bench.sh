#!/bin/sh
/usr/bin/env python -mtimeit -s 'from simplejson.tests.test_pass1 import test_parse' 'test_parse()'
/usr/bin/env python -c 'from simplejson.tests.test_pass1 import test_parse; import profile; profile.run("for i in xrange(100): test_parse()")'
