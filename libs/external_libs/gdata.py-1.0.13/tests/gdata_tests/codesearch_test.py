#!/usr/bin/python
#
# Copyright (C) 2007 Google Inc.
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


__author__ = 'api.jscudder (Jeffrey Scudder)'


import unittest
import gdata.codesearch
import gdata.test_data

class CodeSearchDataTest(unittest.TestCase):

  def setUp(self):
   self.feed = gdata.codesearch.CodesearchFeedFromString(
       gdata.test_data.CODE_SEARCH_FEED)

  def testCorrectXmlConversion(self):
    self.assert_(self.feed.id.text == 
        'http://www.google.com/codesearch/feeds/search?q=malloc')
    self.assert_(len(self.feed.entry) == 10)
    for entry in self.feed.entry:
      if entry.id.text == ('http://www.google.com/codesearch?hl=en&q=+ma'
          'lloc+show:LDjwp-Iqc7U:84hEYaYsZk8:xDGReDhvNi0&sa=N&ct=rx&cd=1'
          '&cs_p=http://www.gnu.org&cs_f=software/autoconf/manual/autoco'
          'nf-2.60/autoconf.html-002&cs_p=http://www.gnu.org&cs_f=softwa'
          're/autoconf/manual/autoconf-2.60/autoconf.html-002#first'):
        self.assert_(len(entry.match) == 4)
        for match in entry.match:
          if match.line_number == '4':
            self.assert_(match.type == 'text/html')
        self.assert_(entry.file.name == 
            'software/autoconf/manual/autoconf-2.60/autoconf.html-002')
        self.assert_(entry.package.name == 'http://www.gnu.org')
        self.assert_(entry.package.uri == 'http://www.gnu.org')

    
if __name__ == '__main__':
  unittest.main()
