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

__author__ = 'api.jscudder (Jeff Scudder)'

import getpass
import unittest
import atom
import gdata.contacts.service


username = ''
password = ''


class ContactsServiceTest(unittest.TestCase):

  def setUp(self):
    self.gd_client = gdata.contacts.service.ContactsService()
    self.gd_client.email = username
    self.gd_client.password = password
    self.gd_client.source = 'GoogleInc-ContactsPythonTest-1'
    self.gd_client.ProgrammaticLogin()

  def testGetContactsFeed(self):
    feed = self.gd_client.GetContactsFeed()
    self.assert_(isinstance(feed, gdata.contacts.ContactsFeed))

  def testCreateUpdateDeleteContact(self):
    # Create a new entry
    new_entry = gdata.contacts.ContactEntry()
    new_entry.title = atom.Title(text='Elizabeth Bennet')
    new_entry.content = atom.Content(text='Test Notes')
    new_entry.email.append(gdata.contacts.Email(
        rel='http://schemas.google.com/g/2005#work',
        primary='true',
        address='liz@gmail.com'))
    new_entry.phone_number.append(gdata.contacts.PhoneNumber(
        rel='http://schemas.google.com/g/2005#work', text='(206)555-1212'))
    new_entry.organization = gdata.contacts.Organization(
        org_name=gdata.contacts.OrgName(text='TestCo.'), 
        rel='http://schemas.google.com/g/2005#work')

    entry = self.gd_client.CreateContact(new_entry, 
        '/m8/feeds/contacts/%s/base' % username)

    # Generate and parse the XML for the new entry.
    self.assertEquals(entry.title.text, new_entry.title.text)
    self.assertEquals(entry.content.text, 'Test Notes')
    self.assertEquals(len(entry.email), 1)
    self.assertEquals(entry.email[0].rel, new_entry.email[0].rel)
    self.assertEquals(entry.email[0].address, 'liz@gmail.com')
    self.assertEquals(len(entry.phone_number), 1)
    self.assertEquals(entry.phone_number[0].rel,
        new_entry.phone_number[0].rel)
    self.assertEquals(entry.phone_number[0].text, '(206)555-1212')
    self.assertEquals(entry.organization.org_name.text, 'TestCo.')

    # Edit the entry.
    entry.phone_number[0].text = '(555)555-1212'
    updated = self.gd_client.UpdateContact(entry.GetEditLink().href, entry)
    self.assertEquals(updated.content.text, 'Test Notes')
    self.assertEquals(len(updated.phone_number), 1)
    self.assertEquals(updated.phone_number[0].rel,
        entry.phone_number[0].rel)
    self.assertEquals(updated.phone_number[0].text, '(555)555-1212')

    # Dekete the entry.
    self.gd_client.DeleteContact(updated.GetEditLink().href)


class ContactsQueryTest(unittest.TestCase):

  def testConvertToString(self):
    query = gdata.contacts.service.ContactsQuery()
    self.assertEquals(str(query), '/m8/feeds/contacts/default/base')
    query.max_results = '10'
    self.assertEquals(query.ToUri(), 
        '/m8/feeds/contacts/default/base?max-results=10')


def DeleteTestContact(client):
  # Get test contact
  feed = client.GetContactsFeed(uri='/m8/feeds/contacts/%s/base' % username)
  for entry in feed.entry:
    if (entry.title.text == 'Elizabeth Bennet' and 
          entry.content.text == 'Test Notes' and 
          entry.email[0].address == 'liz@gmail.com'):
      print 'Deleting test contact'
      client.DeleteContact(entry.GetEditLink().href)
  

if __name__ == '__main__':
  print ('NOTE: Please run these tests only with a test account. ' +
      'The tests may delete or update your data.')
  username = raw_input('Please enter your username: ')
  password = getpass.getpass()
  unittest.main()
