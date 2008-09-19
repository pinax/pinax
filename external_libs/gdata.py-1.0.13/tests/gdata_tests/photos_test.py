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


__author__ = 'api.jscudder (Jeffrey Scudder)'


import unittest
from gdata import test_data
import gdata.photos


class AlbumFeedTest(unittest.TestCase):

  def setUp(self):
    self.album_feed = gdata.photos.AlbumFeedFromString(test_data.ALBUM_FEED)

  def testCorrectXmlParsing(self):
    self.assert_(self.album_feed.id.text == 'http://picasaweb.google.com/data/feed/api/user/sample.user/albumid/1')
    self.assert_(self.album_feed.gphoto_id.text == '1')
    self.assert_(len(self.album_feed.entry) == 4)
    for entry in self.album_feed.entry:
      if entry.id.text == 'http://picasaweb.google.com/data/entry/api/user/sample.user/albumid/1/photoid/2':
        self.assert_(entry.summary.text == 'Blue')


class PhotoFeedTest(unittest.TestCase):

  def setUp(self):
    self.feed = gdata.photos.PhotoFeedFromString(test_data.ALBUM_FEED)

  def testCorrectXmlParsing(self):
    for entry in self.feed.entry:
      if entry.id.text == 'http://picasaweb.google.com/data/entry/api/user/sample.user/albumid/1/photoid/2':
        self.assert_(entry.gphoto_id.text == '2')
        self.assert_(entry.albumid.text == '1')
        self.assert_(entry.exif.flash.text == 'true')
        self.assert_(entry.media.title.type == 'plain')
        self.assert_(entry.media.title.text == 'Aqua Blue.jpg')
        self.assert_(len(entry.media.thumbnail) == 3)



class AnyFeedTest(unittest.TestCase):

  def setUp(self):
    self.feed = gdata.photos.AnyFeedFromString(test_data.ALBUM_FEED)

  def testEntryTypeConversion(self):
    for entry in self.feed.entry:
      if entry.id.text == 'http://picasaweb.google.com/data/feed/api/user/sample.user/albumid/':
        self.assert_(isinstance(entry, gdata.photos.PhotoEntry))


if __name__ == '__main__':
  unittest.main()
