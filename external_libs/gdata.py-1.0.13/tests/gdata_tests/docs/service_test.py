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

__author__ = 'api.jfisher (Jeff Fisher)'

import getpass
import unittest
import StringIO
import gdata.docs.service


username = ''
password = ''


class DocumentListServiceTest(unittest.TestCase):

  def setUp(self):

    self.gd_client = gdata.docs.service.DocsService()
    self.gd_client.email = username
    self.gd_client.password = password
    self.gd_client.source = 'Document List Client Unit Tests'
    self.gd_client.ProgrammaticLogin()
  
  def testGetDocumentsListFeed(self):
    feed = self.gd_client.GetDocumentListFeed()
    self.assert_(isinstance(feed, gdata.docs.DocumentListFeed))

  def testCreateAndDeleteSpreadsheet(self):
    virtual_csv_file = StringIO.StringIO(',,,')
    virtual_media_source = gdata.MediaSource(file_handle=virtual_csv_file, content_type='text/csv', content_length=3)
    entry = self.gd_client.UploadSpreadsheet(virtual_media_source, 'test title')
    self.assertTrue(entry.title.text == 'test title')
    self.gd_client.Delete(entry.GetEditLink().href)


if __name__ == '__main__':
  print ('NOTE: Please run these tests only with a test account. ' +
      'The tests may delete or update your data.')
  username = raw_input('Please enter your username: ')
  password = getpass.getpass()
  unittest.main()
