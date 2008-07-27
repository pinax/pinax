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


__author__ = 'api.jfisher (Jeff Fisher)'


import unittest
from gdata import test_data
import gdata.docs

class DocumentListEntryTest(unittest.TestCase):
  
  def setUp(self):
    self.dl_entry = gdata.docs.DocumentListEntryFromString(
                         test_data.DOCUMENT_LIST_ENTRY)

  def testToAndFromStringWithData(self):

    entry = gdata.docs.DocumentListEntryFromString(str(self.dl_entry))
    
    self.assertEqual(entry.author[0].name.text, 'test.user')
    self.assertEqual(entry.author[0].email.text, 'test.user@gmail.com')
    self.assertEqual(entry.category[0].label, 'spreadsheet')
    self.assertEqual(entry.id.text,
        'http://docs.google.com/feeds/documents/private/full/' +\
        'spreadsheet%3Asupercalifragilisticexpealidocious')
    self.assertEqual(entry.title.text,'Test Spreadsheet')

class DocumentListFeedTest(unittest.TestCase):

  def setUp(self):
    self.dl_feed = gdata.docs.DocumentListFeedFromString(
                        test_data.DOCUMENT_LIST_FEED)

  def testToAndFromString(self):
    self.assert_(len(self.dl_feed.entry) == 2)
    for an_entry in self.dl_feed.entry:
      self.assert_(isinstance(an_entry, gdata.docs.DocumentListEntry))
    new_dl_feed = gdata.docs.DocumentListFeedFromString(str(
                       self.dl_feed))
    for an_entry in new_dl_feed.entry:
      self.assert_(isinstance(an_entry, gdata.docs.DocumentListEntry))

  def testConvertActualData(self):
    for an_entry in self.dl_feed.entry:
      self.assertEqual(an_entry.author[0].name.text, 'test.user')
      self.assertEqual(an_entry.author[0].email.text, 'test.user@gmail.com')
      if(an_entry.category[0].label == 'spreadsheet'):
        self.assertEqual(an_entry.title.text, 'Test Spreadsheet')
      elif(an_entry.category[0].label == 'document'):
        self.assertEqual(an_entry.title.text, 'Test Document')

  def testLinkFinderFindsHtmlLink(self):
    for entry in self.dl_feed.entry:
      # All Document List entries should have a self link
      self.assert_(entry.GetSelfLink() is not None)
      # All Document List entries should have an HTML link
      self.assert_(entry.GetHtmlLink() is not None)


if __name__ == '__main__':
  unittest.main()
