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


__author__ = 'api.jscudder (Jeff Scudder)'


import unittest
import getpass
try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import gdata.base.service
import gdata.service
import atom.service
import gdata.base
import atom
from gdata import test_data


username = ''
password = ''


class GBaseServiceUnitTest(unittest.TestCase):
  
  def setUp(self):
    self.gd_client = gdata.base.service.GBaseService()
    self.gd_client.email = username 
    self.gd_client.password = password 
    self.gd_client.source = 'BaseClient "Unit" Tests'
    self.gd_client.api_key = 'ABQIAAAAoLioN3buSs9KqIIq9VmkFxT2yXp_ZAY8_ufC' +\
                             '3CFXhHIE1NvwkxRK8C1Q8OWhsWA2AIKv-cVKlVrNhQ'

  def tearDown(self):
    # No teardown needed
    pass  

  def testProperties(self):
    email_string = 'Test Email'
    password_string = 'Passwd'
    api_key_string = 'my API key'

    self.gd_client.email = email_string
    self.assertEquals(self.gd_client.email, email_string)
    self.gd_client.password = password_string
    self.assertEquals(self.gd_client.password, password_string)
    self.gd_client.api_key = api_key_string
    self.assertEquals(self.gd_client.api_key, api_key_string)
    self.gd_client.api_key = None
    self.assert_(self.gd_client.api_key is None)

  def testQuery(self):
    my_query = gdata.base.service.BaseQuery(feed='/base/feeds/snippets')
    my_query['max-results'] = '25'
    my_query.bq = 'digital camera [item type: products]'
    result = self.gd_client.Query(my_query.ToUri())
    self.assert_(isinstance(result, atom.Feed))

    service = gdata.base.service.GBaseService(username, password)
    query = gdata.base.service.BaseQuery()
    query.feed = '/base/feeds/snippets'
    query.bq = 'digital camera'
    feed = service.Query(query.ToUri())

  def testQueryWithConverter(self):
    my_query = gdata.base.service.BaseQuery(feed='/base/feeds/snippets')
    my_query['max-results'] = '1'
    my_query.bq = 'digital camera [item type: products]'
    result = self.gd_client.Query(my_query.ToUri(), 
        converter=gdata.base.GBaseSnippetFeedFromString)
    self.assert_(isinstance(result, gdata.base.GBaseSnippetFeed))

  def testCorrectReturnTypes(self):
    q = gdata.base.service.BaseQuery()
    q.feed = '/base/feeds/snippets'
    q.bq = 'digital camera'
    result = self.gd_client.QuerySnippetsFeed(q.ToUri())
    self.assert_(isinstance(result, gdata.base.GBaseSnippetFeed))

    q.feed = '/base/feeds/attributes'
    result = self.gd_client.QueryAttributesFeed(q.ToUri())
    self.assert_(isinstance(result, gdata.base.GBaseAttributesFeed))

    q = gdata.base.service.BaseQuery()
    q.feed = '/base/feeds/itemtypes/en_US'
    result = self.gd_client.QueryItemTypesFeed(q.ToUri())
    self.assert_(isinstance(result, gdata.base.GBaseItemTypesFeed))

    q = gdata.base.service.BaseQuery()
    q.feed = '/base/feeds/locales'
    result = self.gd_client.QueryLocalesFeed(q.ToUri())
    self.assert_(isinstance(result, gdata.base.GBaseLocalesFeed))

  def testInsertItemUpdateItemAndDeleteItem(self):
    try:
      self.gd_client.ProgrammaticLogin()
      self.assert_(self.gd_client.auth_token is not None)
      self.assert_(self.gd_client.captcha_token is None)
      self.assert_(self.gd_client.captcha_url is None)
    except gdata.service.CaptchaRequired:
      self.fail('Required Captcha')
    
    proposed_item = gdata.base.GBaseItemFromString(test_data.TEST_BASE_ENTRY)
    result = self.gd_client.InsertItem(proposed_item)

    item_id = result.id.text
    self.assertEquals(result.id.text != None, True)

    updated_item = gdata.base.GBaseItemFromString(test_data.TEST_BASE_ENTRY)
    updated_item.label[0].text = 'Test Item'
    result = self.gd_client.UpdateItem(item_id, updated_item)

    # Try to update an incorrect item_id.
    try:
      result = self.gd_client.UpdateItem(item_id + '2', updated_item)
      self.fail()
    except gdata.service.RequestError:
      pass

    result = self.gd_client.DeleteItem(item_id)
    self.assert_(result)

    # Delete and already deleted item.
    try:
      result = self.gd_client.DeleteItem(item_id)
      self.fail()
    except gdata.service.RequestError:
      pass

  def testInsertItemUpdateItemAndDeleteItemWithConverter(self):
    try:
      self.gd_client.ProgrammaticLogin()
      self.assert_(self.gd_client.auth_token is not None)
      self.assert_(self.gd_client.captcha_token is None)
      self.assert_(self.gd_client.captcha_url is None)
    except gdata.service.CaptchaRequired:
      self.fail('Required Captcha')

    proposed_item = gdata.base.GBaseItemFromString(test_data.TEST_BASE_ENTRY)
    result = self.gd_client.InsertItem(proposed_item, 
        converter=atom.EntryFromString)
    self.assertEquals(isinstance(result, atom.Entry), True)
    self.assertEquals(isinstance(result, gdata.base.GBaseItem), False)

    item_id = result.id.text
    self.assertEquals(result.id.text != None, True)

    updated_item = gdata.base.GBaseItemFromString(test_data.TEST_BASE_ENTRY)
    updated_item.label[0].text = 'Test Item'
    result = self.gd_client.UpdateItem(item_id, updated_item, 
        converter=atom.EntryFromString)
    self.assertEquals(isinstance(result, atom.Entry), True)
    self.assertEquals(isinstance(result, gdata.base.GBaseItem), False)

    result = self.gd_client.DeleteItem(item_id)
    self.assertEquals(result, True)

  def testMakeBatchRequests(self):
    try:
      self.gd_client.ProgrammaticLogin()
      self.assert_(self.gd_client.auth_token is not None)
      self.assert_(self.gd_client.captcha_token is None)
      self.assert_(self.gd_client.captcha_url is None)
    except gdata.service.CaptchaRequired:
      self.fail('Required Captcha')

    request_feed = gdata.base.GBaseItemFeed(atom_id=atom.Id(
        text='test batch'))
    entry1 = gdata.base.GBaseItemFromString(test_data.TEST_BASE_ENTRY)
    entry1.title.text = 'first batch request item'
    entry2 = gdata.base.GBaseItemFromString(test_data.TEST_BASE_ENTRY)
    entry2.title.text = 'second batch request item'
    request_feed.AddInsert(entry1)
    request_feed.AddInsert(entry2)
    
    result_feed = self.gd_client.ExecuteBatch(request_feed)
    self.assertEquals(result_feed.entry[0].batch_status.code, '201')
    self.assertEquals(result_feed.entry[0].batch_status.reason, 'Created')
    self.assertEquals(result_feed.entry[0].title.text, 'first batch request item')
    self.assertEquals(result_feed.entry[0].item_type.text, 'products')
    self.assertEquals(result_feed.entry[1].batch_status.code, '201')
    self.assertEquals(result_feed.entry[1].batch_status.reason, 'Created')
    self.assertEquals(result_feed.entry[1].title.text, 'second batch request item')

    # Now delete the newly created items.
    request_feed = gdata.base.GBaseItemFeed(atom_id=atom.Id(
        text='test deletions'))
    request_feed.AddDelete(entry=result_feed.entry[0])
    request_feed.AddDelete(entry=result_feed.entry[1])
    self.assertEquals(request_feed.entry[0].batch_operation.type, 
                      gdata.BATCH_DELETE)
    self.assertEquals(request_feed.entry[1].batch_operation.type, 
                      gdata.BATCH_DELETE)
    
    result_feed = self.gd_client.ExecuteBatch(request_feed)
    self.assertEquals(result_feed.entry[0].batch_status.code, '200')
    self.assertEquals(result_feed.entry[0].batch_status.reason, 'Success')
    self.assertEquals(result_feed.entry[0].title.text, 'first batch request item')
    self.assertEquals(result_feed.entry[1].batch_status.code, '200')
    self.assertEquals(result_feed.entry[1].batch_status.reason, 'Success')
    self.assertEquals(result_feed.entry[1].title.text, 'second batch request item')

    
if __name__ == '__main__':
  print ('NOTE: Please run these tests only with a test account. ' +
      'The tests may delete or update your data.')
  username = raw_input('Please enter your username: ')
  password = getpass.getpass()
  unittest.main()
