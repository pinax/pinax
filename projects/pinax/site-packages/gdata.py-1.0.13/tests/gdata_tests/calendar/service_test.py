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

__author__ = 'api.rboyd@google.com (Ryan Boyd)'

import unittest
try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import atom
import gdata.calendar
import gdata.calendar.service
import random
import getpass

# Commented out as dateutil is not in this repository
#from dateutil.parser import parse


username = ''
password = ''


class CalendarServiceUnitTest(unittest.TestCase):
  
  def setUp(self):
    self.cal_client = gdata.calendar.service.CalendarService()
    self.cal_client.email = username 
    self.cal_client.password = password
    self.cal_client.source = 'GCalendarClient "Unit" Tests'

  def tearDown(self):
    # No teardown needed
    pass  

  def testPostUpdateAndDeleteSubscription(self):
    """Test posting a new subscription, updating it, deleting it"""
    self.cal_client.ProgrammaticLogin()

    subscription_id = 'c4o4i7m2lbamc4k26sc2vokh5g%40group.calendar.google.com'
    subscription_url = '%s%s' % (
        'http://www.google.com/calendar/feeds/default/allcalendars/full/', 
        subscription_id)

    # Subscribe to Google Doodles calendar        
    calendar = gdata.calendar.CalendarListEntry()
    calendar.id = atom.Id(text=subscription_id)
    returned_calendar = self.cal_client.InsertCalendarSubscription(calendar)
    self.assertEquals(subscription_url, returned_calendar.id.text)
    self.assertEquals('Google Doodles', returned_calendar.title.text)

    # Update subscription
    calendar_to_update = self.cal_client.GetCalendarListEntry(subscription_url)
    self.assertEquals('Google Doodles', calendar_to_update.title.text) 
    self.assertEquals('true', calendar_to_update.selected.value) 
    calendar_to_update.selected.value = 'false'
    self.assertEquals('false', calendar_to_update.selected.value) 
    updated_calendar = self.cal_client.UpdateCalendar(calendar_to_update)
    self.assertEquals('false', updated_calendar.selected.value) 
    
    # Delete subscription
    response = self.cal_client.DeleteCalendarEntry(
        returned_calendar.GetEditLink().href)
    self.assertEquals(True, response)

  def testPostUpdateAndDeleteCalendar(self):
    """Test posting a new calendar, updating it, deleting it"""
    self.cal_client.ProgrammaticLogin()

    # New calendar to create
    title='Little League Schedule'
    description='This calendar contains practice and game times'
    time_zone='America/Los_Angeles'
    hidden=False
    location='Oakland'
    color='#2952A3'

    # Calendar object
    calendar = gdata.calendar.CalendarListEntry()
    calendar.title = atom.Title(text=title)
    calendar.summary = atom.Summary(text=description)
    calendar.where = gdata.calendar.Where(value_string=location)
    calendar.color = gdata.calendar.Color(value=color)
    calendar.timezone = gdata.calendar.Timezone(value=time_zone)
    if hidden:
      calendar.hidden = gdata.calendar.Hidden(value='true')
    else:
      calendar.hidden = gdata.calendar.Hidden(value='false')

    # Create calendar
    new_calendar = self.cal_client.InsertCalendar(new_calendar=calendar)
    self.assertEquals(title, new_calendar.title.text)
    self.assertEquals(description, new_calendar.summary.text)
    self.assertEquals(location, new_calendar.where.value_string)
    self.assertEquals(color, new_calendar.color.value)
    self.assertEquals(time_zone, new_calendar.timezone.value)
    if hidden:
      self.assertEquals('true', new_calendar.hidden.value) 
    else:
      self.assertEquals('false', new_calendar.hidden.value) 

    # Update calendar
    calendar_to_update = self.cal_client.GetCalendarListEntry(
        new_calendar.id.text)
    updated_title = 'This is the updated title'
    calendar_to_update.title.text = updated_title 
    updated_calendar = self.cal_client.UpdateCalendar(calendar_to_update)
    self.assertEquals(updated_title, updated_calendar.title.text)
   
    # Delete calendar
    calendar_to_delete  = self.cal_client.GetCalendarListEntry(
        new_calendar.id.text)
    self.cal_client.Delete(calendar_to_delete.GetEditLink().href) 

    return new_calendar
    
  def testPostAndDeleteExtendedPropertyEvent(self):
    """Test posting a new entry with an extended property, deleting it"""
    # Get random data for creating event
    r = random.Random()
    r.seed()
    random_event_number = str(r.randint(100000,1000000))
    random_event_title = 'My Random Extended Property Test Event %s' % ( 
        random_event_number)

    # Set event data 
    event = gdata.calendar.CalendarEventEntry()
    event.author.append(atom.Author(name=atom.Name(text='GData Test user')))
    event.title = atom.Title(text=random_event_title)
    event.content = atom.Content(text='Picnic with some lunch')
    event.extended_property.append(gdata.calendar.ExtendedProperty(
        name='prop test name', value='prop test value'))

    # Insert event 
    self.cal_client.ProgrammaticLogin()
    new_event = self.cal_client.InsertEvent(event, 
        '/calendar/feeds/default/private/full')

    self.assertEquals(event.extended_property[0].value,
        new_event.extended_property[0].value)

    # Delete the event
    self.cal_client.DeleteEvent(new_event.GetEditLink().href)

  # WARNING: Due to server-side issues, this test takes a while (~60seconds)
  def testPostEntryWithCommentAndDelete(self):
    """Test posting a new entry with an extended property, deleting it"""
    # Get random data for creating event
    r = random.Random()
    r.seed()
    random_event_number = str(r.randint(100000,1000000))
    random_event_title = 'My Random Comments Test Event %s' % (
        random_event_number)

    # Set event data
    event = gdata.calendar.CalendarEventEntry()
    event.author.append(atom.Author(name=atom.Name(text='GData Test user')))
    event.title = atom.Title(text=random_event_title)
    event.content = atom.Content(text='Picnic with some lunch')

    # Insert event
    self.cal_client.ProgrammaticLogin()
    new_event = self.cal_client.InsertEvent(event,
        '/calendar/feeds/default/private/full')

    # Get comments feed
    comments_url = new_event.comments.feed_link.href
    comments_query = gdata.calendar.service.CalendarEventCommentQuery(comments_url)
    comments_feed = self.cal_client.CalendarQuery(comments_query)

    # Add comment
    comments_entry = gdata.calendar.CalendarEventCommentEntry()
    comments_entry.content = atom.Content(text='Comments content')
    comments_entry.author.append(
        atom.Author(name=atom.Name(text='GData Test user'),
            email=atom.Email(text='gdata.ops.demo@gmail.com')))
    new_comments_entry = self.cal_client.InsertEventComment(comments_entry,
        comments_feed.GetPostLink().href)
  
    # Delete the event
    event_to_delete = self.cal_client.GetCalendarEventEntry(new_event.id.text)
    self.cal_client.DeleteEvent(event_to_delete.GetEditLink().href)

  def testPostQueryUpdateAndDeleteEvents(self):
    """Test posting a new entry, updating it, deleting it, querying for it"""

    # Get random data for creating event
    r = random.Random()
    r.seed()
    random_event_number = str(r.randint(100000,1000000))
    random_event_title = 'My Random Test Event %s' % random_event_number
        
    random_start_hour = (r.randint(1,1000000) % 23)
    random_end_hour = random_start_hour + 1
    non_random_start_minute = 0
    non_random_end_minute = 0
    random_month = (r.randint(1,1000000) % 12 + 1)
    random_day_of_month = (r.randint(1,1000000) % 28 + 1)
    non_random_year = 2008
    start_time = '%04d-%02d-%02dT%02d:%02d:00.000-05:00' % (
        non_random_year, random_month, random_day_of_month,
        random_start_hour, non_random_start_minute,)
    end_time = '%04d-%02d-%02dT%02d:%02d:00.000-05:00' % (
        non_random_year, random_month, random_day_of_month,
        random_end_hour, non_random_end_minute,)

    # Set event data 
    event = gdata.calendar.CalendarEventEntry()
    event.author.append(atom.Author(name=atom.Name(text='GData Test user')))
    event.title = atom.Title(text=random_event_title)
    event.content = atom.Content(text='Picnic with some lunch')
    event.where.append(gdata.calendar.Where(value_string='Down by the river'))
    event.when.append(gdata.calendar.When(start_time=start_time,end_time=end_time))

    # Insert event 
    self.cal_client.ProgrammaticLogin()
    new_event = self.cal_client.InsertEvent(event, 
        '/calendar/feeds/default/private/full')

    # Ensure that atom data returned from calendar server equals atom data sent 
    self.assertEquals(event.title.text, new_event.title.text)
    self.assertEquals(event.content.text, new_event.content.text)

    # Ensure that gd:where data returned from calendar equals value sent
    self.assertEquals(event.where[0].value_string,
        new_event.where[0].value_string)

    # Commented out as dateutil is not in this repository
    # Ensure that dates returned from calendar server equals dates sent 
    #start_time_py = parse(event.when[0].start_time)
    #start_time_py_new = parse(new_event.when[0].start_time)
    #self.assertEquals(start_time_py, start_time_py_new)

    #end_time_py = parse(event.when[0].end_time)
    #end_time_py_new = parse(new_event.when[0].end_time)
    #self.assertEquals(end_time_py, end_time_py_new)

    # Update event
    event_to_update = new_event
    updated_title_text = event_to_update.title.text + ' - UPDATED'
    event_to_update.title = atom.Title(text=updated_title_text)

    updated_event = self.cal_client.UpdateEvent(
        event_to_update.GetEditLink().href, event_to_update)

    # Ensure that updated title was set in the updated event
    self.assertEquals(event_to_update.title.text, updated_event.title.text)

    # Delete the event
    self.cal_client.DeleteEvent(updated_event.GetEditLink().href)

    # Ensure deleted event is marked as canceled in the feed
    after_delete_query = gdata.calendar.service.CalendarEventQuery()
    after_delete_query.updated_min = '2007-01-01'
    after_delete_query.text_query = str(random_event_number) 
    after_delete_query.max_results = '1'
    after_delete_query_result = self.cal_client.CalendarQuery(
        after_delete_query)

    # Ensure feed returned at max after_delete_query.max_results events 
    self.assert_(
        len(after_delete_query_result.entry) <= after_delete_query.max_results)

    # Ensure status of returned event is canceled
    self.assertEquals(after_delete_query_result.entry[0].event_status.value,
        'CANCELED')

  def testCreateAndDeleteEventUsingBatch(self):
    # Get random data for creating event
    r = random.Random()
    r.seed()
    random_event_number = str(r.randint(100000,1000000))
    random_event_title = 'My Random Comments Test Event %s' % (
        random_event_number)

    # Set event data
    event = gdata.calendar.CalendarEventEntry()
    event.author.append(atom.Author(name=atom.Name(text='GData Test user')))
    event.title = atom.Title(text=random_event_title)
    event.content = atom.Content(text='Picnic with some lunch')

    # Form a batch request
    batch_request = gdata.calendar.CalendarEventFeed()
    batch_request.AddInsert(entry=event)

    # Execute the batch request to insert the event.
    self.cal_client.ProgrammaticLogin()
    batch_result = self.cal_client.ExecuteBatch(batch_request, 
        gdata.calendar.service.DEFAULT_BATCH_URL)

    self.assertEquals(len(batch_result.entry), 1)
    self.assertEquals(batch_result.entry[0].title.text, random_event_title)
    self.assertEquals(batch_result.entry[0].batch_operation.type, 
                      gdata.BATCH_INSERT)
    self.assertEquals(batch_result.GetBatchLink().href, 
                      gdata.calendar.service.DEFAULT_BATCH_URL)

    # Create a batch request to delete the newly created entry.
    batch_delete_request = gdata.calendar.CalendarEventFeed()
    batch_delete_request.AddDelete(entry=batch_result.entry[0])
  
    batch_delete_result = self.cal_client.ExecuteBatch(batch_delete_request, 
        batch_result.GetBatchLink().href)
    self.assertEquals(len(batch_delete_result.entry), 1)
    self.assertEquals(batch_delete_result.entry[0].batch_operation.type, 
                      gdata.BATCH_DELETE)

  def testCorrectReturnTypesForGetMethods(self):
    self.cal_client.ProgrammaticLogin()

    result = self.cal_client.GetCalendarEventFeed()
    self.assertEquals(isinstance(result, gdata.calendar.CalendarEventFeed), 
                      True)


class CalendarEventQueryUnitTest(unittest.TestCase):

  def setUp(self):
    self.query = gdata.calendar.service.CalendarEventQuery()

  def testOrderByValidatesValues(self):
    self.query.orderby = 'lastmodified'
    self.assertEquals(self.query.orderby, 'lastmodified')
    try:
      self.query.orderby = 'illegal input'
      self.fail()
    except gdata.calendar.service.Error:
      self.assertEquals(self.query.orderby, 'lastmodified')
      
  def testSortOrderValidatesValues(self):
    self.query.sortorder = 'a'
    self.assertEquals(self.query.sortorder, 'a')
    try:
      self.query.sortorder = 'illegal input'
      self.fail()
    except gdata.calendar.service.Error:
      self.assertEquals(self.query.sortorder, 'a')

  def testTimezoneParameter(self):
    self.query.ctz = 'America/Los_Angeles'
    self.assertEquals(self.query['ctz'], 'America/Los_Angeles')
    self.assert_(self.query.ToUri().find('America%2FLos_Angeles') > -1)


if __name__ == '__main__':
  print ('NOTE: Please run these tests only with a test account. ' +
      'The tests may delete or update your data.')
  username = raw_input('Please enter your username: ')
  password = getpass.getpass()
  unittest.main()
