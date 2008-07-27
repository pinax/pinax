#!/usr/bin/python
#
# Copyright (C) 2008 Google Inc.
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
import atom
import gdata.contacts

class ContactEntryTest(unittest.TestCase):

  def setUp(self):
    self.entry = gdata.contacts.ContactEntryFromString(test_data.NEW_CONTACT)

  def testParsingTestEntry(self):
    self.assertEquals(self.entry.title.text, 'Elizabeth Bennet')
    self.assertEquals(len(self.entry.email), 2)
    for email in self.entry.email:
      if email.rel == 'http://schemas.google.com/g/2005#work':
        self.assertEquals(email.address, 'liz@gmail.com')
      elif email.rel == 'http://schemas.google.com/g/2005#home':
        self.assertEquals(email.address, 'liz@example.org')
    self.assertEquals(len(self.entry.phone_number), 2)
    self.assertEquals(len(self.entry.postal_address), 1)
    self.assertEquals(self.entry.postal_address[0].primary, 'true')
    self.assertEquals(self.entry.postal_address[0].text, 
        '1600 Amphitheatre Pkwy Mountain View')
    self.assertEquals(len(self.entry.im), 1)


  def testToAndFromString(self):
    copied_entry = gdata.contacts.ContactEntryFromString(str(self.entry))   
    self.assertEquals(copied_entry.title.text, 'Elizabeth Bennet')
    self.assertEquals(len(copied_entry.email), 2)
    for email in copied_entry.email:
      if email.rel == 'http://schemas.google.com/g/2005#work':
        self.assertEquals(email.address, 'liz@gmail.com')
      elif email.rel == 'http://schemas.google.com/g/2005#home':
        self.assertEquals(email.address, 'liz@example.org')
    self.assertEquals(len(copied_entry.phone_number), 2)
    self.assertEquals(len(copied_entry.postal_address), 1)
    self.assertEquals(copied_entry.postal_address[0].primary, 'true')
    self.assertEquals(copied_entry.postal_address[0].text, 
        '1600 Amphitheatre Pkwy Mountain View')
    self.assertEquals(len(copied_entry.im), 1)

  def testCreateContactFromScratch(self):
    # Create a new entry
    new_entry = gdata.contacts.ContactEntry()
    new_entry.title = atom.Title(text='Elizabeth Bennet')
    new_entry.content = atom.Content(text='Test Notes')
    new_entry.email.append(gdata.contacts.Email(
        rel='http://schemas.google.com/g/2005#work', 
        address='liz@gmail.com'))
    new_entry.phone_number.append(gdata.contacts.PhoneNumber(
        rel='http://schemas.google.com/g/2005#work', text='(206)555-1212'))
    new_entry.organization = gdata.contacts.Organization(
        org_name=gdata.contacts.OrgName(text='TestCo.'))

    # Generate and parse the XML for the new entry.
    entry_copy = gdata.contacts.ContactEntryFromString(str(new_entry))
    self.assertEquals(entry_copy.title.text, new_entry.title.text)
    self.assertEquals(entry_copy.content.text, 'Test Notes')
    self.assertEquals(len(entry_copy.email), 1)
    self.assertEquals(entry_copy.email[0].rel, new_entry.email[0].rel)
    self.assertEquals(entry_copy.email[0].address, 'liz@gmail.com')
    self.assertEquals(len(entry_copy.phone_number), 1) 
    self.assertEquals(entry_copy.phone_number[0].rel, 
        new_entry.phone_number[0].rel)
    self.assertEquals(entry_copy.phone_number[0].text, '(206)555-1212')
    self.assertEquals(entry_copy.organization.org_name.text, 'TestCo.')


class ContactFeedTest(unittest.TestCase):

  def setUp(self):
    self.feed = gdata.contacts.ContactsFeedFromString(test_data.CONTACTS_FEED)

  def testParsingTestFeed(self):
    self.assertEquals(self.feed.id.text, 
        'http://www.google.com/m8/feeds/contacts/liz%40gmail.com/base')
    self.assertEquals(self.feed.title.text, 'Contacts')
    self.assertEquals(self.feed.total_results.text, '1')
    self.assertEquals(len(self.feed.entry), 1)
    self.assert_(isinstance(self.feed.entry[0], gdata.contacts.ContactEntry))
   
  def testToAndFromString(self):
    copied_feed = gdata.contacts.ContactsFeedFromString(str(self.feed))
    self.assertEquals(copied_feed.id.text, 
        'http://www.google.com/m8/feeds/contacts/liz%40gmail.com/base')
    self.assertEquals(copied_feed.title.text, 'Contacts')
    self.assertEquals(copied_feed.total_results.text, '1')
    self.assertEquals(len(copied_feed.entry), 1)
    self.assert_(isinstance(copied_feed.entry[0], gdata.contacts.ContactEntry))


if __name__ == '__main__':
  unittest.main()
