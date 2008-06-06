#!/usr/bin/python
#
# Copyright (C) 2006 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


__author__ = 'api.jscudder@gmail.com (Jeff Scudder)'


import unittest

class ModuleTestRunner(object):

  def __init__(self, module_list=None, module_settings=None):
    """Constructor for a runner to run tests in the modules listed.

    Args:
      module_list: list (optional) The modules whose test cases will be run.
      module_settings: dict (optional) A dictionary of module level varables
          which should be set in the modules if they are present. An
          example is the username and password which is a module variable
          in most service_test modules.
    """
    self.modules = module_list or []
    self.settings = module_settings or {}

  def RunAllTests(self):
    """Executes all tests in this objects modules list.

    It also sets any module variables which match the settings keys to the
    corresponding values in the settings member.
    """
    runner = unittest.TextTestRunner()
    for module in self.modules:
      # Set any module variables according to the contents in the settings
      for setting, value in self.settings.iteritems():
        try:
          setattr(module, setting, value)
        except AttributeError:
          # This module did not have a variable for the current setting, so
          # we skip it and try the next setting.
          pass
      # We have set all of the applicable settings for the module, now
      # run the tests.
      print '\nRunning all tests in module', module.__name__
      runner.run(unittest.defaultTestLoader.loadTestsFromModule(module))    
