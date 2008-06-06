#!/usr/bin/python
#
# Copyright (C) 2007 SIOS Technology, Inc.
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


__author__ = 'tmatsuo@sios.com (Takashi MATSUO)'

import unittest
try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import atom 
import gdata
from gdata import test_data
import gdata.apps

class AppsEmailListRecipientFeedTest(unittest.TestCase):

  def setUp(self):
    self.rcpt_feed = gdata.apps.EmailListRecipientFeedFromString(
      test_data.EMAIL_LIST_RECIPIENT_FEED)

  def testEmailListRecipientEntryCount(self):
    """Count EmailListRecipient entries in EmailListRecipientFeed"""

    self.assertEquals(len(self.rcpt_feed.entry), 2)

  def testLinkFinderFindsHtmlLink(self):
    """Tests the return value of GetXXXLink() methods"""

    self.assert_(self.rcpt_feed.GetSelfLink() is not None)
    self.assert_(self.rcpt_feed.GetNextLink() is not None)
    self.assert_(self.rcpt_feed.GetEditLink() is None)
    self.assert_(self.rcpt_feed.GetHtmlLink() is None)

  def testStartItem(self):
    """Tests the existence of <openSearch:startIndex> in
    EmailListRecipientFeed and verifies the value"""

    self.assert_(isinstance(self.rcpt_feed.start_index, gdata.StartIndex),
        "EmailListRecipient feed <openSearch:startIndex> element must be " +
        "an instance of gdata.OpenSearch: %s" % self.rcpt_feed.start_index)
    self.assertEquals(self.rcpt_feed.start_index.text, "1")

  def testEmailListRecipientEntries(self):
    """Tests the existence of <atom:entry> in EmailListRecipientFeed
    and simply verifies the value"""

    for a_entry in self.rcpt_feed.entry:
      self.assert_(isinstance(a_entry, gdata.apps.EmailListRecipientEntry),
          "EmailListRecipient Feed <atom:entry> must be an instance of " +
          "apps.EmailListRecipientEntry: %s" % a_entry)

    self.assertEquals(self.rcpt_feed.entry[0].who.email, "joe@example.com")
    self.assertEquals(self.rcpt_feed.entry[1].who.email, "susan@example.com")

class AppsEmailListFeedTest(unittest.TestCase):

  def setUp(self):
    self.list_feed = gdata.apps.EmailListFeedFromString(
      test_data.EMAIL_LIST_FEED)

  def testEmailListEntryCount(self):
    """Count EmailList entries in EmailListFeed"""

    self.assertEquals(len(self.list_feed.entry), 2)

  def testLinkFinderFindsHtmlLink(self):
    """Tests the return value of GetXXXLink() methods"""

    self.assert_(self.list_feed.GetSelfLink() is not None)
    self.assert_(self.list_feed.GetNextLink() is not None)
    self.assert_(self.list_feed.GetEditLink() is None)
    self.assert_(self.list_feed.GetHtmlLink() is None)

  def testStartItem(self):
    """Tests the existence of <openSearch:startIndex> in EmailListFeed
    and verifies the value"""

    self.assert_(isinstance(self.list_feed.start_index, gdata.StartIndex),
        "EmailList feed <openSearch:startIndex> element must be an instance " +
        "of gdata.OpenSearch: %s" % self.list_feed.start_index)
    self.assertEquals(self.list_feed.start_index.text, "1")

  def testUserEntries(self):
    """Tests the existence of <atom:entry> in EmailListFeed and simply
    verifies the value"""

    for a_entry in self.list_feed.entry:
      self.assert_(isinstance(a_entry, gdata.apps.EmailListEntry),
          "EmailList Feed <atom:entry> must be an instance of " +
          "apps.EmailListEntry: %s" % a_entry)

    self.assertEquals(self.list_feed.entry[0].email_list.name, "us-sales")
    self.assertEquals(self.list_feed.entry[1].email_list.name, "us-eng")

class AppsUserFeedTest(unittest.TestCase):

  def setUp(self):
    self.user_feed = gdata.apps.UserFeedFromString(test_data.USER_FEED)

  def testUserEntryCount(self):
    """Count User entries in UserFeed"""

    self.assertEquals(len(self.user_feed.entry), 2)

  def testLinkFinderFindsHtmlLink(self):
    """Tests the return value of GetXXXLink() methods"""

    self.assert_(self.user_feed.GetSelfLink() is not None)
    self.assert_(self.user_feed.GetNextLink() is not None)
    self.assert_(self.user_feed.GetEditLink() is None)
    self.assert_(self.user_feed.GetHtmlLink() is None)

  def testStartItem(self):
    """Tests the existence of <openSearch:startIndex> in UserFeed and
    verifies the value"""

    self.assert_(isinstance(self.user_feed.start_index, gdata.StartIndex),
        "User feed <openSearch:startIndex> element must be an instance " +
        "of gdata.OpenSearch: %s" % self.user_feed.start_index)
    self.assertEquals(self.user_feed.start_index.text, "1")

  def testUserEntries(self):
    """Tests the existence of <atom:entry> in UserFeed and simply
    verifies the value"""

    for a_entry in self.user_feed.entry:
      self.assert_(isinstance(a_entry, gdata.apps.UserEntry),
          "User Feed <atom:entry> must be an instance of " +
          "apps.UserEntry: %s" % a_entry)

    self.assertEquals(self.user_feed.entry[0].login.user_name, "TestUser")
    self.assertEquals(self.user_feed.entry[0].who.email,
                      "TestUser@example.com")
    self.assertEquals(self.user_feed.entry[1].login.user_name, "JohnSmith")
    self.assertEquals(self.user_feed.entry[1].who.email,
                      "JohnSmith@example.com")

class AppsNicknameFeedTest(unittest.TestCase):

  def setUp(self):
    self.nick_feed = gdata.apps.NicknameFeedFromString(test_data.NICK_FEED)

  def testNicknameEntryCount(self):
    """Count Nickname entries in NicknameFeed"""

    self.assertEquals(len(self.nick_feed.entry), 2)

  def testId(self):
    """Tests the existence of <atom:id> in NicknameFeed and verifies
    the value"""

    self.assert_(isinstance(self.nick_feed.id, atom.Id),
        "Nickname feed <atom:id> element must be an instance of " +
        "atom.Id: %s" % self.nick_feed.id)

    self.assertEquals(self.nick_feed.id.text,
                      "http://www.google.com/a/feeds/example.com/nickname/2.0")

  def testStartItem(self):
    """Tests the existence of <openSearch:startIndex> in NicknameFeed
    and verifies the value"""

    self.assert_(isinstance(self.nick_feed.start_index, gdata.StartIndex),
        "Nickname feed <openSearch:startIndex> element must be an instance " +
        "of gdata.OpenSearch: %s" % self.nick_feed.start_index)
    self.assertEquals(self.nick_feed.start_index.text, "1")

  def testItemsPerPage(self):
    """Tests the existence of <openSearch:itemsPerPage> in
    NicknameFeed and verifies the value"""

    self.assert_(isinstance(self.nick_feed.items_per_page, gdata.ItemsPerPage),
        "Nickname feed <openSearch:itemsPerPage> element must be an " +
        "instance of gdata.ItemsPerPage: %s" % self.nick_feed.items_per_page)

    self.assertEquals(self.nick_feed.items_per_page.text, "2")

  def testLinkFinderFindsHtmlLink(self):
    """Tests the return value of GetXXXLink() methods"""

    self.assert_(self.nick_feed.GetSelfLink() is not None)
    self.assert_(self.nick_feed.GetEditLink() is None)
    self.assert_(self.nick_feed.GetHtmlLink() is None)

  def testNicknameEntries(self):
    """Tests the existence of <atom:entry> in NicknameFeed and simply
    verifies the value"""

    for a_entry in self.nick_feed.entry:
      self.assert_(isinstance(a_entry, gdata.apps.NicknameEntry),
          "Nickname Feed <atom:entry> must be an instance of " +
          "apps.NicknameEntry: %s" % a_entry)

    self.assertEquals(self.nick_feed.entry[0].nickname.name, "Foo")
    self.assertEquals(self.nick_feed.entry[1].nickname.name, "Bar")

class AppsEmailListRecipientEntryTest(unittest.TestCase):

  def setUp(self):

    self.rcpt_entry = gdata.apps.EmailListRecipientEntryFromString(
      test_data.EMAIL_LIST_RECIPIENT_ENTRY)

  def testId(self):
    """Tests the existence of <atom:id> in EmailListRecipientEntry and
    verifies the value"""

    self.assert_(
      isinstance(self.rcpt_entry.id, atom.Id),
      "EmailListRecipient entry <atom:id> element must be an instance of " +
      "atom.Id: %s" %
      self.rcpt_entry.id)

    self.assertEquals(
      self.rcpt_entry.id.text,
      'https://www.google.com/a/feeds/example.com/emailList/2.0/us-sales/' +
      'recipient/TestUser%40example.com')

  def testUpdated(self):
    """Tests the existence of <atom:updated> in
    EmailListRecipientEntry and verifies the value"""

    self.assert_(
      isinstance(self.rcpt_entry.updated, atom.Updated),
      "EmailListRecipient entry <atom:updated> element must be an instance " +
      "of atom.Updated: %s" % self.rcpt_entry.updated)

    self.assertEquals(self.rcpt_entry.updated.text,
                      '1970-01-01T00:00:00.000Z')

  def testCategory(self):
    """Tests the existence of <atom:category> in
    EmailListRecipientEntry and verifies the value"""

    for a_category in self.rcpt_entry.category:
      self.assert_(
        isinstance(a_category, atom.Category),
        "EmailListRecipient entry <atom:category> element must be an " +
        "instance of atom.Category: %s" % a_category)

      self.assertEquals(a_category.scheme,
                        "http://schemas.google.com/g/2005#kind")

      self.assertEquals(a_category.term,
                        "http://schemas.google.com/apps/2006#" +
                        "emailList.recipient")

  def testTitle(self):
    """Tests the existence of <atom:title> in EmailListRecipientEntry
    and verifies the value"""

    self.assert_(
      isinstance(self.rcpt_entry.title, atom.Title),
      "EmailListRecipient entry <atom:title> element must be an instance of " +
      "atom.Title: %s" % self.rcpt_entry.title)
      
    self.assertEquals(self.rcpt_entry.title.text, 'TestUser')

  def testLinkFinderFindsHtmlLink(self):
    """Tests the return value of GetXXXLink() methods"""

    self.assert_(self.rcpt_entry.GetSelfLink() is not None)
    self.assert_(self.rcpt_entry.GetEditLink() is not None)
    self.assert_(self.rcpt_entry.GetHtmlLink() is None)

  def testWho(self):
    """Tests the existence of a <gdata:who> in EmailListRecipientEntry
    and verifies the value"""

    self.assert_(isinstance(self.rcpt_entry.who, gdata.apps.Who),
        "EmailListRecipient entry <gdata:who> must be an instance of " +
        "apps.Who: %s" % self.rcpt_entry.who)
    self.assertEquals(self.rcpt_entry.who.email, 'TestUser@example.com')

class AppsEmailListEntryTest(unittest.TestCase):

  def setUp(self):

    self.list_entry = gdata.apps.EmailListEntryFromString(
      test_data.EMAIL_LIST_ENTRY)

  def testId(self):
    """Tests the existence of <atom:id> in EmailListEntry and verifies
    the value"""

    self.assert_(
      isinstance(self.list_entry.id, atom.Id),
      "EmailList entry <atom:id> element must be an instance of atom.Id: %s" %
      self.list_entry.id)

    self.assertEquals(
      self.list_entry.id.text,
      'https://www.google.com/a/feeds/example.com/emailList/2.0/testlist')

  def testUpdated(self):
    """Tests the existence of <atom:updated> in EmailListEntry and
    verifies the value"""

    self.assert_(
      isinstance(self.list_entry.updated, atom.Updated),
      "EmailList entry <atom:updated> element must be an instance of " +
      "atom.Updated: %s" % self.list_entry.updated)

    self.assertEquals(self.list_entry.updated.text,
                      '1970-01-01T00:00:00.000Z')

  def testCategory(self):
    """Tests the existence of <atom:category> in EmailListEntry and
    verifies the value"""

    for a_category in self.list_entry.category:
      self.assert_(
        isinstance(a_category, atom.Category),
        "EmailList entry <atom:category> element must be an instance " +
        "of atom.Category: %s" % a_category)

      self.assertEquals(a_category.scheme,
                        "http://schemas.google.com/g/2005#kind")

      self.assertEquals(a_category.term,
                        "http://schemas.google.com/apps/2006#emailList")

  def testTitle(self):
    """Tests the existence of <atom:title> in EmailListEntry and verifies
    the value"""

    self.assert_(
      isinstance(self.list_entry.title, atom.Title),
      "EmailList entry <atom:title> element must be an instance of " +
      "atom.Title: %s" % self.list_entry.title)
      
    self.assertEquals(self.list_entry.title.text, 'testlist')

  def testLinkFinderFindsHtmlLink(self):
    """Tests the return value of GetXXXLink() methods"""

    self.assert_(self.list_entry.GetSelfLink() is not None)
    self.assert_(self.list_entry.GetEditLink() is not None)
    self.assert_(self.list_entry.GetHtmlLink() is None)

  def testEmailList(self):
    """Tests the existence of a <apps:emailList> in EmailListEntry and
    verifies the value"""

    self.assert_(isinstance(self.list_entry.email_list, gdata.apps.EmailList),
        "EmailList entry <apps:emailList> must be an instance of " +
        "apps.EmailList: %s" % self.list_entry.email_list)
    self.assertEquals(self.list_entry.email_list.name, 'testlist')

  def testFeedLink(self):
    """Test the existence of a <gdata:feedLink> in EmailListEntry and
    verifies the value"""
    
    for an_feed_link in self.list_entry.feed_link:
      self.assert_(isinstance(an_feed_link, gdata.FeedLink),
          "EmailList entry <gdata:feedLink> must be an instance of " +
          "gdata.FeedLink: %s" % an_feed_link)
    self.assertEquals(self.list_entry.feed_link[0].rel,
                      'http://schemas.google.com/apps/2006#' +
                      'emailList.recipients')
    self.assertEquals(self.list_entry.feed_link[0].href,
                      'http://www.google.com/a/feeds/example.com/emailList/' +
                      '2.0/testlist/recipient/')

class AppsNicknameEntryTest(unittest.TestCase):

  def setUp(self):
    self.nick_entry = gdata.apps.NicknameEntryFromString(test_data.NICK_ENTRY)

  def testId(self):
    """Tests the existence of <atom:id> in NicknameEntry and verifies
    the value"""

    self.assert_(
      isinstance(self.nick_entry.id, atom.Id),
      "Nickname entry <atom:id> element must be an instance of atom.Id: %s" %
      self.nick_entry.id)

    self.assertEquals(
      self.nick_entry.id.text,
      'https://www.google.com/a/feeds/example.com/nickname/2.0/Foo')

  def testCategory(self):
    """Tests the existence of <atom:category> in NicknameEntry and
    verifies the value"""

    for a_category in self.nick_entry.category:
      self.assert_(
        isinstance(a_category, atom.Category),
        "Nickname entry <atom:category> element must be an instance " +
        "of atom.Category: %s" % a_category)

      self.assertEquals(a_category.scheme,
                        "http://schemas.google.com/g/2005#kind")

      self.assertEquals(a_category.term,
                        "http://schemas.google.com/apps/2006#nickname")

  def testTitle(self):
    """Tests the existence of <atom:title> in NicknameEntry and
    verifies the value"""

    self.assert_(isinstance(self.nick_entry.title, atom.Title),
        "Nickname entry <atom:title> element must be an instance " +
        "of atom.Title: %s" % self.nick_entry.title)

    self.assertEquals(self.nick_entry.title.text, "Foo")
    
  def testLogin(self):
    """Tests the existence of <apps:login> in NicknameEntry and
    verifies the value"""

    self.assert_(isinstance(self.nick_entry.login, gdata.apps.Login),
        "Nickname entry <apps:login> element must be an instance " +
        "of apps.Login: %s" % self.nick_entry.login)
    self.assertEquals(self.nick_entry.login.user_name, "TestUser")

  def testNickname(self):
    """Tests the existence of <apps:nickname> in NicknameEntry and
    verifies the value"""

    self.assert_(isinstance(self.nick_entry.nickname, gdata.apps.Nickname),
        "Nickname entry <apps:nickname> element must be an instance " +
        "of apps.Nickname: %s" % self.nick_entry.nickname)
    self.assertEquals(self.nick_entry.nickname.name, "Foo")

  def testLinkFinderFindsHtmlLink(self):
    """Tests the return value of GetXXXLink() methods"""

    self.assert_(self.nick_entry.GetSelfLink() is not None)
    self.assert_(self.nick_entry.GetEditLink() is not None)
    self.assert_(self.nick_entry.GetHtmlLink() is None)

class AppsUserEntryTest(unittest.TestCase):

  def setUp(self):
    self.user_entry = gdata.apps.UserEntryFromString(test_data.USER_ENTRY)

  def testId(self):
    """Tests the existence of <atom:id> in UserEntry and verifies the
    value"""

    self.assert_(
      isinstance(self.user_entry.id, atom.Id),
      "User entry <atom:id> element must be an instance of atom.Id: %s" %
      self.user_entry.id)

    self.assertEquals(
      self.user_entry.id.text,
      'https://www.google.com/a/feeds/example.com/user/2.0/TestUser')

  def testUpdated(self):
    """Tests the existence of <atom:updated> in UserEntry and verifies
    the value"""

    self.assert_(
      isinstance(self.user_entry.updated, atom.Updated),
      "User entry <atom:updated> element must be an instance of " +
      "atom.Updated: %s" % self.user_entry.updated)

    self.assertEquals(self.user_entry.updated.text,
                      '1970-01-01T00:00:00.000Z')

  def testCategory(self):
    """Tests the existence of <atom:category> in UserEntry and
    verifies the value"""

    for a_category in self.user_entry.category:
      self.assert_(
        isinstance(a_category, atom.Category),
        "User entry <atom:category> element must be an instance " +
        "of atom.Category: %s" % a_category)

      self.assertEquals(a_category.scheme,
                        "http://schemas.google.com/g/2005#kind")

      self.assertEquals(a_category.term,
                        "http://schemas.google.com/apps/2006#user")

  def testTitle(self):
    """Tests the existence of <atom:title> in UserEntry and verifies
    the value"""

    self.assert_(
      isinstance(self.user_entry.title, atom.Title),
      "User entry <atom:title> element must be an instance of atom.Title: %s" %
      self.user_entry.title)
      
    self.assertEquals(self.user_entry.title.text, 'TestUser')

  def testLinkFinderFindsHtmlLink(self):
    """Tests the return value of GetXXXLink() methods"""

    self.assert_(self.user_entry.GetSelfLink() is not None)
    self.assert_(self.user_entry.GetEditLink() is not None)
    self.assert_(self.user_entry.GetHtmlLink() is None)

  def testLogin(self):
    """Tests the existence of <apps:login> in UserEntry and verifies
    the value"""

    self.assert_(isinstance(self.user_entry.login, gdata.apps.Login),
        "User entry <apps:login> element must be an instance of apps.Login: %s"
        % self.user_entry.login)

    self.assertEquals(self.user_entry.login.user_name, 'TestUser')
    self.assertEquals(self.user_entry.login.password, 'password')
    self.assertEquals(self.user_entry.login.suspended, 'false')
    self.assertEquals(self.user_entry.login.ip_whitelisted, 'false')
    self.assertEquals(self.user_entry.login.hash_function_name, 'SHA-1')

  def testName(self):
    """Tests the existence of <apps:name> in UserEntry and verifies
    the value"""

    self.assert_(isinstance(self.user_entry.name, gdata.apps.Name),
        "User entry <apps:name> element must be an instance of apps.Name: %s"
        % self.user_entry.name)
    self.assertEquals(self.user_entry.name.family_name, 'Test')
    self.assertEquals(self.user_entry.name.given_name, 'User')

  def testQuota(self):
    """Tests the existence of <apps:quota> in UserEntry and verifies
    the value"""

    self.assert_(isinstance(self.user_entry.quota, gdata.apps.Quota),
        "User entry <apps:quota> element must be an instance of apps.Quota: %s"
        % self.user_entry.quota)
    self.assertEquals(self.user_entry.quota.limit, '1024')

  def testFeedLink(self):
    """Test the existence of a <gdata:feedLink> in UserEntry and
    verifies the value"""
    
    for an_feed_link in self.user_entry.feed_link:
      self.assert_(isinstance(an_feed_link, gdata.FeedLink),
          "User entry <gdata:feedLink> must be an instance of gdata.FeedLink" +
          ": %s" % an_feed_link)
    self.assertEquals(self.user_entry.feed_link[0].rel,
                      'http://schemas.google.com/apps/2006#user.nicknames')
    self.assertEquals(self.user_entry.feed_link[0].href,
                      'https://www.google.com/a/feeds/example.com/nickname/' +
                      '2.0?username=Test-3121')
    self.assertEquals(self.user_entry.feed_link[1].rel,
                      'http://schemas.google.com/apps/2006#user.emailLists')
    self.assertEquals(self.user_entry.feed_link[1].href,
                      'https://www.google.com/a/feeds/example.com/emailList/' +
                      '2.0?recipient=testlist@example.com')

  def testUpdate(self):
    """Tests for modifing attributes of UserEntry"""

    self.user_entry.name.family_name = 'ModifiedFamilyName'
    self.user_entry.name.given_name = 'ModifiedGivenName'
    self.user_entry.quota.limit = '2048'
    self.user_entry.login.password = 'ModifiedPassword'
    self.user_entry.login.suspended = 'true'
    modified = gdata.apps.UserEntryFromString(self.user_entry.ToString())

    self.assertEquals(modified.name.family_name, 'ModifiedFamilyName')
    self.assertEquals(modified.name.given_name, 'ModifiedGivenName')
    self.assertEquals(modified.quota.limit, '2048')
    self.assertEquals(modified.login.password, 'ModifiedPassword')
    self.assertEquals(modified.login.suspended, 'true')
    
if __name__ == '__main__':
  unittest.main()

