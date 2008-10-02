#!/usr/bin/python

import sys
import unittest
import module_test_runner
import getopt
import getpass
# Modules whose tests we will run.
import gdata_test
import atom_test
import gdata_tests.apps_test
import gdata_tests.base_test
import gdata_tests.calendar_test
import gdata_tests.docs_test
import gdata_tests.spreadsheet_test
import gdata_tests.auth_test
import gdata_tests.photos_test
import gdata_tests.codesearch_test


def RunAllTests():
  test_runner = module_test_runner.ModuleTestRunner()
  test_runner.modules = [gdata_test, atom_test, gdata_tests.apps_test, 
                         gdata_tests.base_test, gdata_tests.calendar_test, 
                         gdata_tests.docs_test, gdata_tests.spreadsheet_test,
                         gdata_tests.auth_test, gdata_tests.photos_test,
                         gdata_tests.codesearch_test]
  test_runner.RunAllTests()
  
if __name__ == '__main__':
  RunAllTests()
