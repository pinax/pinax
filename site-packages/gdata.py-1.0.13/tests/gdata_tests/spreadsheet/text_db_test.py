#!/usr/bin/python
#
# Copyright Google 2007-2008, all rights reserved.
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


import unittest
import getpass
import gdata.spreadsheet.text_db
import gdata.spreadsheet.service


__author__ = 'api.jscudder (Jeffrey Scudder)'


username = ''
password = ''


class FactoryTest(unittest.TestCase):

  def setUp(self):
    self.client = gdata.spreadsheet.text_db.DatabaseClient()

  def testBadCredentials(self):
    try:
      self.client.SetCredentials('foo', 'bar')
      self.fail()
    except gdata.spreadsheet.text_db.Error, e:
      pass

  def testCreateGetAndDeleteDatabase(self):
    db_title = 'google_spreadsheets_db unit test 1'
    self.client.SetCredentials(username, password)
    db = self.client.CreateDatabase(db_title)
    # Test finding the database using the name
    db_list = self.client.GetDatabases(name=db_title)
    self.assertTrue(len(db_list) >= 1)
    if len(db_list) >= 1:
      self.assertTrue(db_list[0].entry.title.text == db_title)
    # Test finding the database using the spreadsheet key
    db_list = self.client.GetDatabases(spreadsheet_key=db.spreadsheet_key)
    self.assertTrue(len(db_list) == 1)
    self.assertTrue(db_list[0].entry.title.text == db_title)
    # Delete the test spreadsheet
    db.Delete()


class DatabaseTest(unittest.TestCase):

  def setUp(self):
    client = gdata.spreadsheet.text_db.DatabaseClient(username, password)
    self.db = client.CreateDatabase('google_spreadsheets_db unit test 2')

  def tearDown(self):
    self.db.Delete()

  def testCreateGetAndDeleteTable(self):
    table = self.db.CreateTable('test1', ['1','2','3'])
    # Try to get the new table using the worksheet id.
    table_list = self.db.GetTables(worksheet_id=table.worksheet_id)
    self.assertTrue(len(table_list) == 1)
    self.assertTrue(table_list[0].entry.title.text, 'test1')
    # Try to get the table using the name
    table_list = self.db.GetTables(name='test1')
    self.assertTrue(len(table_list) == 1)
    self.assertTrue(table_list[0].entry.title.text, 'test1')
    # Delete the table
    table.Delete()


class TableTest(unittest.TestCase):
  
  def setUp(self):
    client = gdata.spreadsheet.text_db.DatabaseClient(username, password)
    self.db = client.CreateDatabase('google_spreadsheets_db unit test 3')
    self.table = self.db.CreateTable('test1', ['a','b','c_d','a', 'd:e'])

  def tearDown(self):
    self.db.Delete()

  def testCreateGetAndDeleteRecord(self):
    new_record = self.table.AddRecord({'a':'test1', 'b':'test2', 'cd':'test3', 'a_2':'test4', 'de':'test5'})
    # Test getting record by line number.
    record = self.table.GetRecord(row_number=1)
    self.assertTrue(record is not None)
    self.assertTrue(record.content['a'] == 'test1')
    self.assertTrue(record.content['b'] == 'test2')
    self.assertTrue(record.content['cd'] == 'test3')
    self.assertTrue(record.content['a_2'] == 'test4')
    # Test getting record using the id.
    record_list = self.table.GetRecord(row_id=new_record.row_id)
    self.assertTrue(record is not None)
    # Delete the record.
    new_record.Delete()

  def testPushPullSyncing(self):
    # Get two copies of the same row.
    first_copy = self.table.AddRecord({'a':'1', 'b':'2', 'cd':'3', 'a_2':'4', 'de':'5'})
    second_copy = self.table.GetRecord(first_copy.row_id)

    # Make changes in the first copy
    first_copy.content['a'] = '7'
    first_copy.content['b'] = '9'
    
    # Try to get the changes before they've been committed
    second_copy.Pull()
    self.assertTrue(second_copy.content['a'] == '1')
    self.assertTrue(second_copy.content['b'] == '2')

    # Commit the changes, the content should now be different
    first_copy.Push()
    second_copy.Pull()
    self.assertTrue(second_copy.content['a'] == '7')
    self.assertTrue(second_copy.content['b'] == '9')

    # Make changes to the second copy, push, then try to push changes from
    # the first copy.
    first_copy.content['a'] = '10'
    second_copy.content['a'] = '15'
    first_copy.Push()
    try:
      second_copy.Push()
      # The second update should raise and exception due to a 409 conflict.
      self.fail()
    except gdata.spreadsheet.service.RequestError:
      pass
    except Exception, error:
      #TODO: Why won't the except RequestError catch this?
      pass

  def testFindRecords(self):
    # Add lots of test records:
    self.table.AddRecord({'a':'1', 'b':'2', 'cd':'3', 'a_2':'4', 'de':'5'})
    self.table.AddRecord({'a':'hi', 'b':'2', 'cd':'20', 'a_2':'4', 'de':'5'})
    self.table.AddRecord({'a':'2', 'b':'2', 'cd':'3'})
    self.table.AddRecord({'a':'2', 'b':'2', 'cd':'15', 'de':'7'})
    self.table.AddRecord({'a':'hi hi hi', 'b':'2', 'cd':'15', 'de':'7'})
    self.table.AddRecord({'a':'"5"', 'b':'5', 'cd':'15', 'de':'7'})
    self.table.AddRecord({'a':'5', 'b':'5', 'cd':'15', 'de':'7'})

    matches = self.table.FindRecords('a == 1')
    self.assertTrue(len(matches) == 1)
    self.assertTrue(matches[0].content['a'] == '1')
    self.assertTrue(matches[0].content['b'] == '2')

    matches = self.table.FindRecords('a > 1 && cd < 20')
    self.assertTrue(len(matches) == 4)
    matches = self.table.FindRecords('cd < de')
    self.assertTrue(len(matches) == 7)
    self.assertTrue(len(matches) == 1)
    matches = self.table.FindRecords('a == b')
    self.assertTrue(len(matches) == 0)
    matches = self.table.FindRecords('a == 5')
    self.assertTrue(len(matches) == 1)

  def testIterateResultSet(self):
    # Populate the table with test data.
    self.table.AddRecord({'a':'1', 'b':'2', 'cd':'3', 'a_2':'4', 'de':'5'})
    self.table.AddRecord({'a':'hi', 'b':'2', 'cd':'20', 'a_2':'4', 'de':'5'})
    self.table.AddRecord({'a':'2', 'b':'2', 'cd':'3'})
    self.table.AddRecord({'a':'2', 'b':'2', 'cd':'15', 'de':'7'})
    self.table.AddRecord({'a':'hi hi hi', 'b':'2', 'cd':'15', 'de':'7'})
    self.table.AddRecord({'a':'"5"', 'b':'5', 'cd':'15', 'de':'7'})
    self.table.AddRecord({'a':'5', 'b':'5', 'cd':'15', 'de':'7'})

    # Get the first two rows.
    records = self.table.GetRecords(1, 2)
    self.assertTrue(len(records) == 2)
    self.assertTrue(records[0].content['a'] == '1')
    self.assertTrue(records[1].content['a'] == 'hi')

    # Then get the next two rows.
    next_records = records.GetNext()
    self.assertTrue(len(next_records) == 2)
    self.assertTrue(next_records[0].content['a'] == '2')
    self.assertTrue(next_records[0].content['cd'] == '3')
    self.assertTrue(next_records[1].content['cd'] == '15')
    self.assertTrue(next_records[1].content['de'] == '7')

  def testLookupFieldsOnPreexistingTable(self):
    existing_table = self.db.GetTables(name='test1')[0]
    existing_table.LookupFields()
    self.assertEquals(existing_table.fields, ['a', 'b', 'cd', 'a_2', 'de'])


if __name__ == '__main__':
  if not username:
    username = raw_input('Please enter your username: ')
  if not password:
    password = getpass.getpass()  
  unittest.main()
