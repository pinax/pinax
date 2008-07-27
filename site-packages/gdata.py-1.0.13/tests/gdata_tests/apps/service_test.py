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

__author__ = 'tmatsuo@sios.com (Takashi Matsuo)'

import unittest
try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import atom
import gdata.apps
import gdata.apps.service
import getpass
import time


apps_domain = ''
apps_username = ''
apps_password = ''


class AppsServiceUnitTest01(unittest.TestCase):
  
  def setUp(self):
    self.postfix = time.strftime("%Y%m%d%H%M%S")
    email = apps_username + '@' + apps_domain
    self.apps_client = gdata.apps.service.AppsService(
      email=email, domain=apps_domain, password=apps_password,
      source='AppsClient "Unit" Tests')
    self.apps_client.ProgrammaticLogin()
    self.created_user = None

  def tearDown(self):
    if self.created_user is not None:
      try:
        self.apps_client.DeleteUser(self.created_user.login.user_name)
      except Exception, e:
        pass

  def test001RetrieveUser(self):
    """Tests RetrieveUser method"""

    try:
      self_user_entry = self.apps_client.RetrieveUser(apps_username)
    except:
      self.fail('Unexpected exception occurred')
    self.assert_(isinstance(self_user_entry, gdata.apps.UserEntry),
        "The return value of RetrieveUser() must be an instance of " +
        "apps.UserEntry: %s" % self_user_entry)
    self.assertEquals(self_user_entry.login.user_name, apps_username)

  def test002RetrieveUserRaisesException(self):
    """Tests if RetrieveUser() raises AppsForYourDomainException with
    appropriate error code"""

    try:
      non_existance = self.apps_client.RetrieveUser('nobody-' + self.postfix)
    except gdata.apps.service.AppsForYourDomainException, e:
      self.assertEquals(e.error_code, gdata.apps.service.ENTITY_DOES_NOT_EXIST)
    except Exception, e:
      self.fail('Unexpected exception occurred: %s' % e)
    else:
      self.fail('No exception occurred')

  def testSuspendAndRestoreUser(self):
    # Create a test user
    user_name = 'an-apps-service-test-account-' + self.postfix
    family_name = 'Tester'
    given_name = 'Apps'
    password = '123$$abc'
    suspended = 'false'

    created_user = self.apps_client.CreateUser(
        user_name=user_name, family_name=family_name, given_name=given_name,
        password=password, suspended=suspended)

    # Suspend then restore the new user.
    entry = self.apps_client.SuspendUser(created_user.login.user_name)
    self.assertEquals(entry.login.suspended, 'true')
    entry = self.apps_client.RestoreUser(created_user.login.user_name)
    self.assertEquals(entry.login.suspended, 'false')

    # Clean up, delete the test user.
    self.apps_client.DeleteUser(user_name)

  def test003MethodsForUser(self):
    """Tests methods for user"""

    user_name = 'TakashiMatsuo-' + self.postfix
    family_name = 'Matsuo'
    given_name = 'Takashi'
    password = '123$$abc'
    suspended = 'false'

    try:
      created_user = self.apps_client.CreateUser(
        user_name=user_name, family_name=family_name, given_name=given_name,
        password=password, suspended=suspended)
    except Exception, e:
      self.assert_(False, 'Unexpected exception occurred: %s' % e)

    self.created_user = created_user
    self.assertEquals(created_user.login.user_name, user_name)
    self.assertEquals(created_user.login.suspended, suspended)
    self.assertEquals(created_user.name.family_name, family_name)
    self.assertEquals(created_user.name.given_name, given_name)

    # self.assertEquals(created_user.quota.limit,
    #                   gdata.apps.service.DEFAULT_QUOTA_LIMIT)

    """Tests RetrieveAllUsers method"""

    try:
      user_feed = self.apps_client.RetrieveAllUsers()
    except Exception, e:
      self.assert_(False, 'Unexpected exception occurred: %s' % e)

    succeed = False
    for a_entry in user_feed.entry:
      if a_entry.login.user_name == user_name:
        succeed = True
    self.assert_(succeed, 'There must be a user: %s' % user_name)

    """Tests UpdateUser method"""

    new_family_name = 'NewFamilyName'
    new_given_name = 'NewGivenName'
    new_quota = '4096'

    created_user.name.family_name = new_family_name
    created_user.name.given_name = new_given_name
    created_user.quota.limit = new_quota
    created_user.login.suspended = 'true'

    try:
      new_user_entry = self.apps_client.UpdateUser(user_name, created_user)
    except Exception, e:
      self.fail('Unexpected exception occurred: %s' % e)
    
    self.assert_(isinstance(new_user_entry, gdata.apps.UserEntry),
        "new user entry must be an instance of gdata.apps.UserEntry: %s"
        % new_user_entry)
    self.assertEquals(new_user_entry.name.family_name, new_family_name)
    self.assertEquals(new_user_entry.name.given_name, new_given_name)
    self.assertEquals(new_user_entry.login.suspended, 'true')

    # quota limit update does not always success.
    # self.assertEquals(new_user_entry.quota.limit, new_quota)

    nobody = gdata.apps.UserEntry()
    nobody.login = gdata.apps.Login(user_name='nobody-' + self.postfix)
    nobody.name = gdata.apps.Name(family_name='nobody', given_name='nobody')

    # make sure that there is no account with nobody- + self.postfix
    try:
      tmp_entry = self.apps_client.RetrieveUser('nobody-' + self.postfix)
    except gdata.apps.service.AppsForYourDomainException, e:
      self.assertEquals(e.error_code, gdata.apps.service.ENTITY_DOES_NOT_EXIST)
    except Exception, e:
      self.fail('Unexpected exception occurred: %s' % e)
    else:
      self.fail('No exception occurred')

    # make sure that UpdateUser fails with AppsForYourDomainException.
    try:
      new_user_entry = self.apps_client.UpdateUser('nobody-' + self.postfix,
                                                   nobody)
    except gdata.apps.service.AppsForYourDomainException, e:
      self.assertEquals(e.error_code, gdata.apps.service.ENTITY_DOES_NOT_EXIST)
    except Exception, e:
      self.fail('Unexpected exception occurred: %s' % e)
    else:
      self.fail('No exception occurred')

    """Tests DeleteUser method"""

    try:
      self.apps_client.DeleteUser(user_name)
    except Exception, e:
      self.assert_(False, 'Unexpected exception occurred: %s' % e)

    # make sure that the account deleted
    try:
      self.apps_client.RetrieveUser(user_name)
    except gdata.apps.service.AppsForYourDomainException, e:
      self.assertEquals(e.error_code, gdata.apps.service.ENTITY_DOES_NOT_EXIST)
    except Exception, e:
      self.fail('Unexpected exception occurred: %s' % e)
    else:
      self.fail('No exception occurred')
    self.created_user = None
      
    # make sure that DeleteUser fails with AppsForYourDomainException.
    try:
      self.apps_client.DeleteUser(user_name)
    except gdata.apps.service.AppsForYourDomainException, e:
      self.assertEquals(e.error_code, gdata.apps.service.ENTITY_DOES_NOT_EXIST)
    except Exception, e:
      self.fail('Unexpected exception occurred: %s' % e)
    else:
      self.fail('No exception occurred')

  def test004MethodsForNickname(self):
    """Tests methods for nickname"""

    # first create a user account
    user_name = 'EmmyMatsuo-' + self.postfix
    family_name = 'Matsuo'
    given_name = 'Emmy'
    password = '123$$abc'
    suspended = 'false'

    try:
      created_user = self.apps_client.CreateUser(
        user_name=user_name, family_name=family_name, given_name=given_name,
        password=password, suspended=suspended)
    except Exception, e:
      self.fail('Unexpected exception occurred: %s' % e)

    self.created_user = created_user
    # tests CreateNickname method
    nickname = 'emmy-' + self.postfix
    try:
      created_nickname = self.apps_client.CreateNickname(user_name, nickname)
    except Exception, e:
      self.fail('Unexpected exception occurred: %s' % e)

    self.assert_(isinstance(created_nickname, gdata.apps.NicknameEntry),
        "Return value of CreateNickname method must be an instance of " +
        "gdata.apps.NicknameEntry: %s" % created_nickname)
    self.assertEquals(created_nickname.login.user_name, user_name)
    self.assertEquals(created_nickname.nickname.name, nickname)

    # tests RetrieveNickname method
    retrieved_nickname = self.apps_client.RetrieveNickname(nickname)
    self.assert_(isinstance(retrieved_nickname, gdata.apps.NicknameEntry),
        "Return value of RetrieveNickname method must be an instance of " +
        "gdata.apps.NicknameEntry: %s" % retrieved_nickname)
    self.assertEquals(retrieved_nickname.login.user_name, user_name)
    self.assertEquals(retrieved_nickname.nickname.name, nickname)

    # tests RetrieveNicknames method
    nickname_feed = self.apps_client.RetrieveNicknames(user_name)
    self.assert_(isinstance(nickname_feed, gdata.apps.NicknameFeed),
        "Return value of RetrieveNicknames method must be an instance of " +
        "gdata.apps.NicknameFeed: %s" % nickname_feed)
    self.assertEquals(nickname_feed.entry[0].login.user_name, user_name)
    self.assertEquals(nickname_feed.entry[0].nickname.name, nickname)

    # tests RetrieveAllNicknames method
    nickname_feed = self.apps_client.RetrieveAllNicknames()
    self.assert_(isinstance(nickname_feed, gdata.apps.NicknameFeed),
        "Return value of RetrieveAllNicknames method must be an instance of " +
        "gdata.apps.NicknameFeed: %s" % nickname_feed)
    succeed = False
    for a_entry in nickname_feed.entry:
      if a_entry.login.user_name == user_name and \
             a_entry.nickname.name == nickname:
        succeed = True
    self.assert_(succeed,
                 "There must be a nickname entry named %s." % nickname)

    # tests DeleteNickname method
    self.apps_client.DeleteNickname(nickname)
    try:
      non_existence = self.apps_client.RetrieveNickname(nickname)
    except gdata.apps.service.AppsForYourDomainException, e:
      self.assertEquals(e.error_code, gdata.apps.service.ENTITY_DOES_NOT_EXIST)
    except Exception, e:
      self.fail('Unexpected exception occurred: %s' % e)
    else:
      self.fail('No exception occurred')

class AppsServiceUnitTest02(unittest.TestCase):
  
  def setUp(self):
    self.postfix = time.strftime("%Y%m%d%H%M%S")
    email = apps_username + '@' + apps_domain
    self.apps_client = gdata.apps.service.AppsService(
      email=email, domain=apps_domain, password=apps_password,
      source='AppsClient "Unit" Tests')
    self.apps_client.ProgrammaticLogin()
    self.created_users = []
    self.created_email_lists = []

  def tearDown(self):
    for user in self.created_users:
      try:
        self.apps_client.DeleteUser(user.login.user_name)
      except Exception, e:
        print e
    for email_list in self.created_email_lists:
      try:
        self.apps_client.DeleteEmailList(email_list.email_list.name)
      except Exception, e:
        print e

  def test001MethodsForEmaillist(self):
    """Tests methods for emaillist """
    
    user_name = 'YujiMatsuo-' + self.postfix
    family_name = 'Matsuo'
    given_name = 'Yuji'
    password = '123$$abc'
    suspended = 'false'

    try:
      user_yuji = self.apps_client.CreateUser(
        user_name=user_name, family_name=family_name, given_name=given_name,
        password=password, suspended=suspended)
    except Exception, e:
      self.fail('Unexpected exception occurred: %s' % e)

    self.created_users.append(user_yuji)

    user_name = 'TaroMatsuo-' + self.postfix
    family_name = 'Matsuo'
    given_name = 'Taro'
    password = '123$$abc'
    suspended = 'false'

    try:
      user_taro = self.apps_client.CreateUser(
        user_name=user_name, family_name=family_name, given_name=given_name,
        password=password, suspended=suspended)
    except Exception, e:
      self.fail('Unexpected exception occurred: %s' % e)

    self.created_users.append(user_taro)

    # tests CreateEmailList method
    list_name = 'list01-' + self.postfix
    try:
      created_email_list = self.apps_client.CreateEmailList(list_name)
    except Exception, e:
      self.fail('Unexpected exception occurred: %s' % e)

    self.assert_(isinstance(created_email_list, gdata.apps.EmailListEntry),
        "Return value of CreateEmailList method must be an instance of " +
        "EmailListEntry: %s" % created_email_list)
    self.assertEquals(created_email_list.email_list.name, list_name)
    self.created_email_lists.append(created_email_list)

    # tests AddRecipientToEmailList method
    try:
      recipient = self.apps_client.AddRecipientToEmailList(
        user_yuji.login.user_name + '@' + apps_domain,
        list_name)
    except Exception, e:
      self.fail('Unexpected exception occurred: %s' % e)

    self.assert_(isinstance(recipient, gdata.apps.EmailListRecipientEntry),
        "Return value of AddRecipientToEmailList method must be an instance " +
        "of EmailListRecipientEntry: %s" % recipient)
    self.assertEquals(recipient.who.email, 
                      user_yuji.login.user_name + '@' + apps_domain)

    try:
      recipient = self.apps_client.AddRecipientToEmailList(
        user_taro.login.user_name + '@' + apps_domain,
        list_name)
    except Exception, e:
      self.fail('Unexpected exception occurred: %s' % e)

    # tests RetrieveAllRecipients method
    try:
      recipient_feed = self.apps_client.RetrieveAllRecipients(list_name)
    except Exception, e:
      self.fail('Unexpected exception occurred: %s' % e)

    self.assert_(isinstance(recipient_feed, gdata.apps.EmailListRecipientFeed),
        "Return value of RetrieveAllRecipients method must be an instance " +
        "of EmailListRecipientFeed: %s" % recipient_feed)
    self.assertEquals(len(recipient_feed.entry), 2)

    # tests RemoveRecipientFromEmailList method
    try:
      self.apps_client.RemoveRecipientFromEmailList(
        user_taro.login.user_name + '@' + apps_domain, list_name)
    except Exception, e:
      self.fail('Unexpected exception occurred: %s' % e)

    # make sure that removal succeeded.
    try:
      recipient_feed = self.apps_client.RetrieveAllRecipients(list_name)
    except Exception, e:
      self.fail('Unexpected exception occurred: %s' % e)

    self.assert_(isinstance(recipient_feed, gdata.apps.EmailListRecipientFeed),
        "Return value of RetrieveAllRecipients method must be an instance " +
        "of EmailListRecipientFeed: %s" % recipient_feed)
    self.assertEquals(len(recipient_feed.entry), 1)

    # tests RetrieveAllEmailLists
    try:
      list_feed = self.apps_client.RetrieveAllEmailLists()
    except Exception, e:
      self.fail('Unexpected exception occurred: %s' % e)
    self.assert_(isinstance(list_feed, gdata.apps.EmailListFeed),
        "Return value of RetrieveAllEmailLists method must be an instance" +
        "of EmailListFeed: %s" % list_feed)
    succeed = False
    for email_list in list_feed.entry:
      if email_list.email_list.name == list_name:
        succeed = True
    self.assert_(succeed, "There must be an email list named %s" % list_name)
    
    # tests RetrieveEmailLists method.
    try:
      list_feed = self.apps_client.RetrieveEmailLists(
        user_yuji.login.user_name + '@' + apps_domain)
    except Exception, e:
      self.fail('Unexpected exception occurred: %s' % e)
    self.assert_(isinstance(list_feed, gdata.apps.EmailListFeed),
        "Return value of RetrieveEmailLists method must be an instance" +
        "of EmailListFeed: %s" % list_feed)
    succeed = False
    for email_list in list_feed.entry:
      if email_list.email_list.name == list_name:
        succeed = True
    self.assert_(succeed, "There must be an email list named %s" % list_name)

  def testRetrieveEmailList(self):
    new_list = self.apps_client.CreateEmailList('my_testing_email_list')
    retrieved_list = self.apps_client.RetrieveEmailList('my_testing_email_list')
    self.assertEquals(new_list.title.text, retrieved_list.title.text)
    self.assertEquals(new_list.id.text, retrieved_list.id.text)
    self.assertEquals(new_list.email_list.name, retrieved_list.email_list.name)

    self.apps_client.DeleteEmailList('my_testing_email_list')

    # Should not be able to retrieve the deleted list.
    try:
      removed_list = self.apps_client.RetrieveEmailList('my_testing_email_list')
      self.fail()
    except gdata.apps.service.AppsForYourDomainException:
      pass


class AppsServiceUnitTest03(unittest.TestCase):
  
  def setUp(self):
    self.postfix = time.strftime("%Y%m%d%H%M%S")
    email = apps_username + '@' + apps_domain
    self.apps_client = gdata.apps.service.AppsService(
      email=email, domain=apps_domain, password=apps_password,
      source='AppsClient "Unit" Tests')
    self.apps_client.ProgrammaticLogin()
    self.created_users = []
    self.created_email_lists = []

  def tearDown(self):
    for user in self.created_users:
      try:
        self.apps_client.DeleteUser(user.login.user_name)
      except Exception, e:
        print e
    for email_list in self.created_email_lists:
      try:
        self.apps_client.DeleteEmailList(email_list.email_list.name)
      except Exception, e:
        print e

  def test001Pagenation(self):
    """Tests for pagination. It takes toooo long."""

    list_feed = self.apps_client.RetrieveAllEmailLists()
    quantity = len(list_feed.entry)
    list_nums = 101
    for i in range(list_nums):
      list_name = 'list%03d-' % i + self.postfix
      #print 'creating list named:', list_name
      try:
        created_email_list = self.apps_client.CreateEmailList(list_name)
      except Exception, e:
        self.fail('Unexpected exception occurred: %s' % e)
      self.created_email_lists.append(created_email_list)

    list_feed = self.apps_client.RetrieveAllEmailLists()
    self.assertEquals(len(list_feed.entry), list_nums + quantity)

if __name__ == '__main__':
  print ('NOTE: Please run these tests only with a test domain. ' +
         'The tests may delete or update your domain\'s account data.')
  apps_domain = raw_input('Please enter your domain: ')
  apps_username = raw_input('Please enter your username of admin account: ')
  apps_password = getpass.getpass()
  unittest.main()
