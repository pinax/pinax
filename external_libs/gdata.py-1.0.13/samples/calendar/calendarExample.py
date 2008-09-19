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


__author__ = 'api.rboyd@gmail.com (Ryan Boyd)'


try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import gdata.calendar.service
import gdata.service
import atom.service
import gdata.calendar
import atom
import getopt
import sys
import string
import time


class CalendarExample:

  def __init__(self, email, password):
    """Creates a CalendarService and provides ClientLogin auth details to it.
    The email and password are required arguments for ClientLogin.  The 
    CalendarService automatically sets the service to be 'cl', as is 
    appropriate for calendar.  The 'source' defined below is an arbitrary 
    string, but should be used to reference your name or the name of your
    organization, the app name and version, with '-' between each of the three
    values.  The account_type is specified to authenticate either 
    Google Accounts or Google Apps accounts.  See gdata.service or 
    http://code.google.com/apis/accounts/AuthForInstalledApps.html for more
    info on ClientLogin.  NOTE: ClientLogin should only be used for installed 
    applications and not for multi-user web applications."""

    self.cal_client = gdata.calendar.service.CalendarService()
    self.cal_client.email = email
    self.cal_client.password = password
    self.cal_client.source = 'Google-Calendar_Python_Sample-1.0'
    self.cal_client.ProgrammaticLogin()

  def _PrintUserCalendars(self): 
    """Retrieves the list of calendars to which the authenticated user either
    owns or subscribes to.  This is the same list as is represented in the 
    Google Calendar GUI.  Although we are only printing the title of the 
    calendar in this case, other information, including the color of the
    calendar, the timezone, and more.  See CalendarListEntry for more details
    on available attributes."""

    feed = self.cal_client.GetAllCalendarsFeed()
    print 'Printing allcalendars: %s' % feed.title.text
    for i, a_calendar in zip(xrange(len(feed.entry)), feed.entry):
      print '\t%s. %s' % (i, a_calendar.title.text,)

  def _PrintOwnCalendars(self):
    """Retrieves the list of calendars to which the authenticated user 
    owns -- 
    Although we are only printing the title of the 
    calendar in this case, other information, including the color of the
    calendar, the timezone, and more.  See CalendarListEntry for more details
    on available attributes."""

    feed = self.cal_client.GetOwnCalendarsFeed()
    print 'Printing owncalendars: %s' % feed.title.text
    for i, a_calendar in zip(xrange(len(feed.entry)), feed.entry):
      print '\t%s. %s' % (i, a_calendar.title.text,)

  def _PrintAllEventsOnDefaultCalendar(self):
    """Retrieves all events on the primary calendar for the authenticated user.
    In reality, the server limits the result set intially returned.  You can 
    use the max_results query parameter to allow the server to send additional
    results back (see query parameter use in DateRangeQuery for more info).
    Additionally, you can page through the results returned by using the 
    feed.GetNextLink().href value to get the location of the next set of
    results."""
  
    feed = self.cal_client.GetCalendarEventFeed()
    print 'Events on Primary Calendar: %s' % (feed.title.text,)
    for i, an_event in zip(xrange(len(feed.entry)), feed.entry):
      print '\t%s. %s' % (i, an_event.title.text,)
      for p, a_participant in zip(xrange(len(an_event.who)), an_event.who):
        print '\t\t%s. %s' % (p, a_participant.email,)
        print '\t\t\t%s' % (a_participant.name,)
        print '\t\t\t%s' % (a_participant.attendee_status.value,)

  def _FullTextQuery(self, text_query='Tennis'):
    """Retrieves events from the calendar which match the specified full-text
    query.  The full-text query searches the title and content of an event,
    but it does not search the value of extended properties at the time of
    this writing.  It uses the default (primary) calendar of the authenticated
    user and uses the private visibility/full projection feed.  Please see:
    http://code.google.com/apis/calendar/reference.html#Feeds 
    for more information on the feed types.  Note: as we're not specifying
    any query parameters other than the full-text query, recurring events
    returned will not have gd:when elements in the response.  Please see
    the Google Calendar API query paramters reference for more info:
    http://code.google.com/apis/calendar/reference.html#Parameters"""

    print 'Full text query for events on Primary Calendar: \'%s\'' % (
        text_query,)
    query = gdata.calendar.service.CalendarEventQuery('default', 'private', 
        'full', text_query)
    feed = self.cal_client.CalendarQuery(query)
    for i, an_event in zip(xrange(len(feed.entry)), feed.entry):
      print '\t%s. %s' % (i, an_event.title.text,)
      print '\t\t%s. %s' % (i, an_event.content.text,)
      for a_when in an_event.when:
        print '\t\tStart time: %s' % (a_when.start_time,)
        print '\t\tEnd time:   %s' % (a_when.end_time,)

  def _DateRangeQuery(self, start_date='2007-01-01', end_date='2007-07-01'):
    """Retrieves events from the server which occur during the specified date
    range.  This uses the CalendarEventQuery class to generate the URL which is
    used to retrieve the feed.  For more information on valid query parameters,
    see: http://code.google.com/apis/calendar/reference.html#Parameters"""

    print 'Date range query for events on Primary Calendar: %s to %s' % (
        start_date, end_date,)
    query = gdata.calendar.service.CalendarEventQuery('default', 'private', 
        'full')
    query.start_min = start_date
    query.start_max = end_date 
    feed = self.cal_client.CalendarQuery(query)
    for i, an_event in zip(xrange(len(feed.entry)), feed.entry):
      print '\t%s. %s' % (i, an_event.title.text,)
      for a_when in an_event.when:
        print '\t\tStart time: %s' % (a_when.start_time,)
        print '\t\tEnd time:   %s' % (a_when.end_time,)

  def _InsertCalendar(self, title='Little League Schedule',
      description='This calendar contains practice and game times',
      time_zone='America/Los_Angeles', hidden=False, location='Oakland',
      color='#2952A3'): 
    """Creates a new calendar using the specified data."""
    print 'Creating new calendar with title "%s"' % title
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

    new_calendar = self.cal_client.InsertCalendar(new_calendar=calendar)
    return new_calendar

  def _UpdateCalendar(self, calendar, title='New Title', color=None):
    """Updates the title and, optionally, the color of the supplied calendar"""
    print 'Updating the calendar titled "%s" with the title "%s"' % (
        calendar.title.text, title)
    calendar.title = atom.Title(text=title)
    if color is not None:
      calendar.color = gdata.calendar.Color(value=color)

    updated_calendar = self.cal_client.UpdateCalendar(calendar=calendar) 
    return updated_calendar

  def _DeleteAllCalendars(self):
    """Deletes all calendars.  Note: the primary calendar cannot be deleted"""
    feed = self.cal_client.GetOwnCalendarsFeed()
    for entry in feed.entry:
      print 'Deleting calendar: %s' % entry.title.text
      try:
        self.cal_client.Delete(entry.GetEditLink().href)
      except gdata.service.RequestError, msg:
        if msg[0]['body'].startswith('Cannot remove primary calendar'):
            print '\t%s' % msg[0]['body']
        else:
            print '\tUnexpected Error: %s' % msg[0]['body']

  def _InsertSubscription(self, 
      id='c4o4i7m2lbamc4k26sc2vokh5g%40group.calendar.google.com'):
    """Subscribes to the calendar with the specified ID."""
    print 'Subscribing to the calendar with ID: %s' % id
    calendar = gdata.calendar.CalendarListEntry()
    calendar.id = atom.Id(text=id)
    returned_calendar = self.cal_client.InsertCalendarSubscription(calendar)
    return returned_calendar

  def _UpdateCalendarSubscription(self, 
      id='c4o4i7m2lbamc4k26sc2vokh5g%40group.calendar.google.com', 
      color=None, hidden=None, selected=None):
    """Updates the subscription to the calendar with the specified ID."""
    print 'Updating the calendar subscription with ID: %s' % id
    calendar_url = (
      'http://www.google.com/calendar/feeds/default/allcalendars/full/%s' % id) 
    calendar_entry = self.cal_client.GetCalendarListEntry(calendar_url)

    if color is not None:
      calendar_entry.color = gdata.calendar.Color(value=color)
    if hidden is not None:
      if hidden:
        calendar_entry.hidden = gdata.calendar.Hidden(value='true')
      else:
        calendar_entry.hidden = gdata.calendar.Hidden(value='false')
    if selected is not None:
      if selected:
        calendar_entry.selected = gdata.calendar.Selected(value='true')
      else:
        calendar_entry.selected = gdata.calendar.Selected(value='false')

    updated_calendar = self.cal_client.UpdateCalendar(
        calendar_entry)
    return updated_calendar

  def _DeleteCalendarSubscription(self, 
      id='c4o4i7m2lbamc4k26sc2vokh5g%40group.calendar.google.com'):
    """Deletes the subscription to the calendar with the specified ID."""
    print 'Deleting the calendar subscription with ID: %s' % id
    calendar_url = (
      'http://www.google.com/calendar/feeds/default/allcalendars/full/%s' % id)
    calendar_entry = self.cal_client.GetCalendarListEntry(calendar_url)
    self.cal_client.DeleteCalendarEntry(calendar_entry.GetEditLink().href)

  def _InsertEvent(self, title='Tennis with Beth', 
      content='Meet for a quick lesson', where='On the courts',
      start_time=None, end_time=None, recurrence_data=None):
    """Inserts a basic event using either start_time/end_time definitions
    or gd:recurrence RFC2445 icalendar syntax.  Specifying both types of
    dates is not valid.  Note how some members of the CalendarEventEntry
    class use arrays and others do not.  Members which are allowed to occur
    more than once in the calendar or GData "kinds" specifications are stored
    as arrays.  Even for these elements, Google Calendar may limit the number
    stored to 1.  The general motto to use when working with the Calendar data
    API is that functionality not available through the GUI will not be 
    available through the API.  Please see the GData Event "kind" document:
    http://code.google.com/apis/gdata/elements.html#gdEventKind
    for more information"""
    
    event = gdata.calendar.CalendarEventEntry()
    event.title = atom.Title(text=title)
    event.content = atom.Content(text=content)
    event.where.append(gdata.calendar.Where(value_string=where))

    if recurrence_data is not None:
      # Set a recurring event
      event.recurrence = gdata.calendar.Recurrence(text=recurrence_data)
    else:
      if start_time is None:
        # Use current time for the start_time and have the event last 1 hour
        start_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
        end_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', 
            time.gmtime(time.time() + 3600))
      event.when.append(gdata.calendar.When(start_time=start_time, 
          end_time=end_time))
    
    new_event = self.cal_client.InsertEvent(event, 
        '/calendar/feeds/default/private/full')
    
    return new_event
   
  def _InsertSingleEvent(self, title='One-time Tennis with Beth',
      content='Meet for a quick lesson', where='On the courts',
      start_time=None, end_time=None):
    """Uses the _InsertEvent helper method to insert a single event which
    does not have any recurrence syntax specified."""

    new_event = self._InsertEvent(title, content, where, start_time, end_time, 
        recurrence_data=None)

    print 'New single event inserted: %s' % (new_event.id.text,)
    print '\tEvent edit URL: %s' % (new_event.GetEditLink().href,)
    print '\tEvent HTML URL: %s' % (new_event.GetHtmlLink().href,)

    return new_event

  def _InsertRecurringEvent(self, title='Weekly Tennis with Beth',
      content='Meet for a quick lesson', where='On the courts',
      recurrence_data=None):
    """Uses the _InsertEvent helper method to insert a recurring event which
    has only RFC2445 icalendar recurrence syntax specified.  Note the use of
    carriage return/newline pairs at the end of each line in the syntax.  Even 
    when specifying times (as opposed to only dates), VTIMEZONE syntax is not
    required if you use a standard Java timezone ID.  Please see the docs for
    more information on gd:recurrence syntax:
    http://code.google.com/apis/gdata/elements.html#gdRecurrence
    """ 

    if recurrence_data is None:
      recurrence_data = ('DTSTART;VALUE=DATE:20070501\r\n'
        + 'DTEND;VALUE=DATE:20070502\r\n'
        + 'RRULE:FREQ=WEEKLY;BYDAY=Tu;UNTIL=20070904\r\n')

    new_event = self._InsertEvent(title, content, where, 
        recurrence_data=recurrence_data, start_time=None, end_time=None)
    
    print 'New recurring event inserted: %s' % (new_event.id.text,)
    print '\tEvent edit URL: %s' % (new_event.GetEditLink().href,)
    print '\tEvent HTML URL: %s' % (new_event.GetHtmlLink().href,)
  
    return new_event

  def _InsertQuickAddEvent(self, 
      content="Tennis with John today 3pm-3:30pm"):
    """Creates an event with the quick_add property set to true so the content
    is processed as quick add content instead of as an event description."""
    event = gdata.calendar.CalendarEventEntry()
    event.content = atom.Content(text=content)
    event.quick_add = gdata.calendar.QuickAdd(value='true');

    new_event = self.cal_client.InsertEvent(event, 
        '/calendar/feeds/default/private/full')
    return new_event
    
  def _InsertSimpleWebContentEvent(self):
    """Creates a WebContent object and embeds it in a WebContentLink.
    The WebContentLink is appended to the existing list of links in the event
    entry.  Finally, the calendar client inserts the event."""

    # Create a WebContent object
    url = 'http://www.google.com/logos/worldcup06.gif'
    web_content = gdata.calendar.WebContent(url=url, width='276', height='120')
    
    # Create a WebContentLink object that contains the WebContent object
    title = 'World Cup'
    href = 'http://www.google.com/calendar/images/google-holiday.gif'
    type = 'image/gif'
    web_content_link = gdata.calendar.WebContentLink(title=title, href=href, 
        link_type=type, web_content=web_content)
        
    # Create an event that contains this web content
    event = gdata.calendar.CalendarEventEntry()
    event.link.append(web_content_link)

    print 'Inserting Simple Web Content Event'
    new_event = self.cal_client.InsertEvent(event, 
        '/calendar/feeds/default/private/full')
    return new_event

  def _InsertWebContentGadgetEvent(self):
    """Creates a WebContent object and embeds it in a WebContentLink.
    The WebContentLink is appended to the existing list of links in the event
    entry.  Finally, the calendar client inserts the event.  Web content
    gadget events display Calendar Gadgets inside Google Calendar."""

    # Create a WebContent object
    url = 'http://google.com/ig/modules/datetime.xml'
    web_content = gdata.calendar.WebContent(url=url, width='300', height='136')
    web_content.gadget_pref.append(
        gdata.calendar.WebContentGadgetPref(name='color', value='green'))

    # Create a WebContentLink object that contains the WebContent object
    title = 'Date and Time Gadget'
    href = 'http://gdata.ops.demo.googlepages.com/birthdayicon.gif'
    type = 'application/x-google-gadgets+xml'
    web_content_link = gdata.calendar.WebContentLink(title=title, href=href,
        link_type=type, web_content=web_content)

    # Create an event that contains this web content
    event = gdata.calendar.CalendarEventEntry()
    event.link.append(web_content_link)

    print 'Inserting Web Content Gadget Event'
    new_event = self.cal_client.InsertEvent(event,
        '/calendar/feeds/default/private/full')
    return new_event

  def _UpdateTitle(self, event, new_title='Updated event title'):
    """Updates the title of the specified event with the specified new_title.
    Note that the UpdateEvent method (like InsertEvent) returns the 
    CalendarEventEntry object based upon the data returned from the server
    after the event is inserted.  This represents the 'official' state of
    the event on the server.  The 'edit' link returned in this event can
    be used for future updates.  Due to the use of the 'optimistic concurrency'
    method of version control, most GData services do not allow you to send 
    multiple update requests using the same edit URL.  Please see the docs:
    http://code.google.com/apis/gdata/reference.html#Optimistic-concurrency
    """

    previous_title = event.title.text
    event.title.text = new_title
    print 'Updating title of event from:\'%s\' to:\'%s\'' % (
        previous_title, event.title.text,) 
    return self.cal_client.UpdateEvent(event.GetEditLink().href, event)

  def _AddReminder(self, event, minutes=10):
    """Adds a reminder to the event.  This uses the default reminder settings
    for the user to determine what type of notifications are sent (email, sms,
    popup, etc.) and sets the reminder for 'minutes' number of minutes before
    the event.  Note: you can only use values for minutes as specified in the
    Calendar GUI."""

    for a_when in event.when:
      if len(a_when.reminder) > 0:
        a_when.reminder[0].minutes = minutes
      else:
        a_when.reminder.append(gdata.calendar.Reminder(minutes=minutes))

    print 'Adding %d minute reminder to event' % (minutes,)
    return self.cal_client.UpdateEvent(event.GetEditLink().href, event)

  def _AddExtendedProperty(self, event, 
      name='http://www.example.com/schemas/2005#mycal.id', value='1234'):
    """Adds an arbitrary name/value pair to the event.  This value is only
    exposed through the API.  Extended properties can be used to store extra
    information needed by your application.  The recommended format is used as
    the default arguments above.  The use of the URL format is to specify a 
    namespace prefix to avoid collisions between different applications."""

    event.extended_property.append(
        gdata.calendar.ExtendedProperty(name=name, value=value))  
    print 'Adding extended property to event: \'%s\'=\'%s\'' % (name, value,)
    return self.cal_client.UpdateEvent(event.GetEditLink().href, event)

  def _DeleteEvent(self, event):
    """Given an event object returned for the calendar server, this method
    deletes the event.  The edit link present in the event is the URL used
    in the HTTP DELETE request."""

    self.cal_client.DeleteEvent(event.GetEditLink().href)

  def _PrintAclFeed(self):
    """Sends a HTTP GET to the default ACL URL 
    (http://www.google.com/calendar/feeds/default/acl/full) and displays the
    feed returned in the response."""
    
    feed = self.cal_client.GetCalendarAclFeed()
    print feed.title.text
    for i, a_rule in zip(xrange(len(feed.entry)), feed.entry):
      print '\t%s. %s' % (i, a_rule.title.text,)
      print '\t\t Role: %s' % (a_rule.role.value,)
      print '\t\t Scope %s - %s' % (a_rule.scope.type, a_rule.scope.value)
    
  def _CreateAclRule(self, username):      
    """Creates a ACL rule that grants the given user permission to view 
    free/busy information on the default calendar.  Note: It is not necessary 
    to specify a title for the ACL entry.  The server will set this to be the
    value of the role specified (in this case "freebusy")."""
    
    rule = gdata.calendar.CalendarAclEntry()
    rule.scope = gdata.calendar.Scope(value=username, scope_type="user")
    roleValue = "http://schemas.google.com/gCal/2005#%s" % ("freebusy")
    rule.role = gdata.calendar.Role(value=roleValue)
    aclUrl = "/calendar/feeds/default/acl/full"
    returned_rule = self.cal_client.InsertAclEntry(rule, aclUrl)
  
  def _RetrieveAclRule(self, username):
    """Builds the aclEntryUri or the entry created in the previous example.
    The sends a HTTP GET message and displays the entry returned in the 
    response."""
    
    aclEntryUri = "http://www.google.com/calendar/feeds/"
    aclEntryUri += "default/acl/full/user:%s" % (username)
    entry = self.cal_client.GetCalendarAclEntry(aclEntryUri)
    print '\t%s' % (entry.title.text,)
    print '\t\t Role: %s' % (entry.role.value,)
    print '\t\t Scope %s - %s' % (entry.scope.type, entry.scope.value)
    return entry

  def _UpdateAclRule(self, entry):
    """Modifies the value of the role in the given entry and POSTs the updated
    entry.  Note that while the role of an ACL entry can be updated, the 
    scope can not be modified."""
     
    roleValue = "http://schemas.google.com/gCal/2005#%s" % ("read")
    entry.role = gdata.calendar.Role(value=roleValue)
    returned_rule = self.cal_client.UpdateAclEntry(entry.GetEditLink().href, 
        entry)
  
  def _DeleteAclRule(self, entry):
    """Given an ACL entry returned for the calendar server, this method
    deletes the entry.  The edit link present in the entry is the URL used
    in the HTTP DELETE request."""
    
    self.cal_client.DeleteAclEntry(entry.GetEditLink().href)

  def Run(self, delete='false'):
    """Runs each of the example methods defined above.  Note how the result
    of the _InsertSingleEvent call is used for updating the title and the
    result of updating the title is used for inserting the reminder and 
    again with the insertion of the extended property.  This is due to the
    Calendar's use of GData's optimistic concurrency versioning control system:
    http://code.google.com/apis/gdata/reference.html#Optimistic-concurrency
    """

    # Getting feeds and query results
    self._PrintUserCalendars()
    self._PrintOwnCalendars()
    self._PrintAllEventsOnDefaultCalendar()
    self._FullTextQuery()
    self._DateRangeQuery()
    
    # Inserting and updating events
    see = self._InsertSingleEvent()
    see_u_title = self._UpdateTitle(see, 'New title for single event')
    see_u_reminder = self._AddReminder(see_u_title, minutes=30)
    see_u_ext_prop = self._AddExtendedProperty(see_u_reminder, 
        name='propname', value='propvalue')
    ree = self._InsertRecurringEvent()
    simple_web_content_event = self._InsertSimpleWebContentEvent()
    web_content_gadget_event = self._InsertWebContentGadgetEvent()
    quick_add_event = self._InsertQuickAddEvent()
  
    # Access Control List examples
    self._PrintAclFeed()
    self._CreateAclRule("user@gmail.com")
    entry = self._RetrieveAclRule("user@gmail.com")
    self._UpdateAclRule(entry)
    self._DeleteAclRule(entry)

    # Creating, updating and deleting calendars
    inserted_calendar = self._InsertCalendar()
    updated_calendar = self._UpdateCalendar(calendar=inserted_calendar) 
    
    # Insert Subscription
    inserted_subscription = self._InsertSubscription()
    updated_subscription = self._UpdateCalendarSubscription(selected=False)
    
    # Delete entries if delete argument='true'
    if delete == 'true':
      print 'Deleting created events'
      self.cal_client.DeleteEvent(see_u_ext_prop.GetEditLink().href)
      self.cal_client.DeleteEvent(ree.GetEditLink().href)
      self.cal_client.DeleteEvent(simple_web_content_event.GetEditLink().href)
      self.cal_client.DeleteEvent(web_content_gadget_event.GetEditLink().href)
      self.cal_client.DeleteEvent(quick_add_event.GetEditLink().href)
      print 'Deleting subscriptions'
      self._DeleteCalendarSubscription()
      print 'Deleting all calendars'
      self._DeleteAllCalendars()
    
 
def main():
  """Runs the CalendarExample application with the provided username and
  and password values.  Authentication credentials are required.  
  NOTE: It is recommended that you run this sample using a test account."""

  # parse command line options
  try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["user=", "pw=", "delete="])
  except getopt.error, msg:
    print ('python calendarExample.py --user [username] --pw [password] ' + 
        '--delete [true|false] ')
    sys.exit(2)

  user = ''
  pw = ''
  delete = 'false'

  # Process options
  for o, a in opts:
    if o == "--user":
      user = a
    elif o == "--pw":
      pw = a
    elif o == "--delete":
      delete = a

  if user == '' or pw == '':
    print ('python calendarExample.py --user [username] --pw [password] ' + 
        '--delete [true|false] ')
    sys.exit(2)

  sample = CalendarExample(user, pw)
  sample.Run(delete)

if __name__ == '__main__':
  main()
