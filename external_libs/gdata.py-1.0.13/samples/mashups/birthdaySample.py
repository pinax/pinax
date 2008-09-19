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
#
#
# This sample uses the Google Spreadsheets data API and the Google 
# Calendar data API. The script pulls a list of birthdays from a 
# Google Spreadsheet and inserts them as webContent events in the
# user's Google Calendar. 
# 
# The script expects a certain format in the spreadsheet: Name,
# Birthday, Photo URL, and Edit URL as headers. Expected format 
# of the birthday is: MM/DD. Edit URL is to be left blank by the
# user - the script uses this column to determine whether to insert
# a new event or to update an event at the URL. 
# 
# See the spreadsheet below for an example:
# http://spreadsheets.google.com/pub?key=pfMX-JDVnx47J0DxqssIQHg
#


__author__ = 'api.stephaniel@google.com (Stephanie Liu)'

try:
  from xml.etree import ElementTree # for Python 2.5 users
except:  
  from elementtree import ElementTree

import gdata.spreadsheet.service
import gdata.calendar.service
import gdata.calendar
import gdata.service
import atom.service
import gdata.spreadsheet
import atom
import string
import time
import datetime
import getopt
import getpass
import sys


class BirthdaySample:
  # CONSTANTS: Expected column headers: name, birthday, photourl, editurl &
  # default calendar reminder set to 2 days
  NAME = "name"
  BIRTHDAY = "birthday"
  PHOTO_URL = "photourl"
  EDIT_URL = "editurl"
  REMINDER = 60 * 24 * 2 # minutes

  def __init__(self, email, password):
    """ Initializes spreadsheet and calendar clients.
        
        Creates SpreadsheetsService and CalendarService objects and 
        authenticates to each with ClientLogin. For more information
        about ClientLogin authentication: 
        http://code.google.com/apis/accounts/AuthForInstalledApps.html

        Args:
          email: string
          password: string
    """

    self.s_client = gdata.spreadsheet.service.SpreadsheetsService()
    self.s_client.email = email
    self.s_client.password = password
    self.s_client.source = 'exampleCo-birthdaySample-1'
    self.s_client.ProgrammaticLogin()

    self.c_client = gdata.calendar.service.CalendarService()
    self.c_client.email = email
    self.c_client.password = password
    self.c_client.source = 'exampleCo-birthdaySample-1'
    self.c_client.ProgrammaticLogin()
  
  def _PrintFeed(self, feed):
    """ Prints out Spreadsheet feeds in human readable format.
      
        Generic function taken from spreadsheetsExample.py.          

        Args:
          feed: SpreadsheetsCellsFeed, SpreadsheetsListFeed,
            SpreadsheetsWorksheetsFeed, or SpreadsheetsSpreadsheetsFeed
    """
    for i, entry in enumerate(feed.entry):
      if isinstance(feed, gdata.spreadsheet.SpreadsheetsCellsFeed):
        print '%s %s\n' % (entry.title.text, entry.content.text)
      elif isinstance(feed, gdata.spreadsheet.SpreadsheetsListFeed):
        print '%s %s %s\n' % (i, entry.title.text, entry.content.text)
      else:
        print '%s %s\n' % (i, entry.title.text)

  def _PromptForSpreadsheet(self):
    """ Prompts user to select spreadsheet.
     
        Gets and displays titles of all spreadsheets for user to 
        select. Generic function taken from spreadsheetsExample.py.

        Args:
          none

        Returns:
           spreadsheet ID that the user selected: string
    """

    feed = self.s_client.GetSpreadsheetsFeed()
    self._PrintFeed(feed)
    input = raw_input('\nSelection: ')
    
    # extract and return the spreadsheet ID
    return feed.entry[string.atoi(input)].id.text.rsplit('/', 1)[1]

  def _PromptForWorksheet(self, key):
    """ Prompts user to select desired worksheet.

        Gets and displays titles of all worksheets for user to
        select. Generic function taken from spreadsheetsExample.py.

        Args:
          key: string

        Returns:
           the worksheet ID that the user selected: string
    """

    feed = self.s_client.GetWorksheetsFeed(key)
    self._PrintFeed(feed)
    input = raw_input('\nSelection: ')

    # extract and return the worksheet ID
    return feed.entry[string.atoi(input)].id.text.rsplit('/', 1)[1]

  def _AddReminder(self, event, minutes):
    """ Adds a reminder to a calendar event. 

        This function sets the reminder attribute of the CalendarEventEntry.
        The script sets it to 2 days by default, and this value is not 
        settable by the user. However, it can easily be changed to take this
        option.

        Args:
          event: CalendarEventEntry
          minutes: int
 
        Returns:
          the updated event: CalendarEventEntry
    """

    for a_when in event.when:
      if len(a_when.reminder) > 0:
        a_when.reminder[0].minutes = minutes
      else:
        a_when.reminder.append(gdata.calendar.Reminder(minutes=minutes))

    return self.c_client.UpdateEvent(event.GetEditLink().href, event)

  def _CreateBirthdayWebContentEvent(self, name, birthday, photo_url):
    """ Create the birthday web content event.

        This function creates and populates a CalendarEventEntry. webContent
        specific attributes are set. To learn more about the webContent
        format:

        http://www.google.com/support/calendar/bin/answer.py?answer=48528

        Args:
          name: string
          birthday: string - expected format (MM/DD)
          photo_url: string     

        Returns:
           the webContent CalendarEventEntry
    """   

    title = "%s's Birthday!" % name
    content = "It's %s's Birthday!" % name
    month = string.atoi(birthday.split("/")[0])
    day = string.atoi(birthday.split("/")[1])

    # Get current year
    year = time.ctime()[-4:]
    year = string.atoi(year)
    
    # Calculate the "end date" for the all day event
    start_time = datetime.date(year, month, day)
    one_day = datetime.timedelta(days=1)
    end_time = start_time + one_day

    start_time_str = start_time.strftime("%Y-%m-%d")
    end_time_str = end_time.strftime("%Y-%m-%d")

    # Create yearly recurrence rule
    recurrence_data = ("DTSTART;VALUE=DATE:%s\r\n"
        "DTEND;VALUE=DATE:%s\r\n"
        "RRULE:FREQ=YEARLY;WKST=SU\r\n" % 
        (start_time.strftime("%Y%m%d"), end_time.strftime("%Y%m%d")))
 
    web_rel = "http://schemas.google.com/gCal/2005/webContent"
    icon_href = "http://www.perstephanie.com/images/birthdayicon.gif"
    icon_type = "image/gif"
    extension_text = (
        'gCal:webContent xmlns:gCal="http://schemas.google.com/gCal/2005"'
        ' url="%s" width="300" height="225"' % (photo_url))

    event = gdata.calendar.CalendarEventEntry()
    event.title = atom.Title(text=title)
    event.content = atom.Content(text=content)
    event.recurrence = gdata.calendar.Recurrence(text=recurrence_data)
    event.when.append(gdata.calendar.When(start_time=start_time_str, 
        end_time=end_time_str))

    # Adding the webContent specific XML 
    event.link.append(atom.Link(rel=web_rel, title=title, href=icon_href, 
        link_type=icon_type))
    event.link[0].extension_elements.append(
        atom.ExtensionElement(extension_text))
 
    return event

  def _InsertBirthdayWebContentEvent(self, event):
    """ Insert event into the authenticated user's calendar. 

        Args:
          event: CalendarEventEntry

        Returns:
           the newly created CalendarEventEntry 
    """

    edit_uri = '/calendar/feeds/default/private/full'
    return self.c_client.InsertEvent(event, edit_uri)

  def Run(self):
    """ Run sample.
 
        TODO: add exception handling 

        Args:
          none
    """
     
    key_id = self._PromptForSpreadsheet()
    wksht_id = self._PromptForWorksheet(key_id)
 
    feed = self.s_client.GetListFeed(key_id, wksht_id) 

    found_name = False
    found_birthday = False
    found_photourl = False
    found_editurl = False 

    # Check to make sure all headers are present
    # Need to find at least one instance of name, birthday, photourl
    # editurl 
    if len(feed.entry) > 0:
      for name, custom in feed.entry[0].custom.iteritems():
        if custom.column == self.NAME:
          found_name = True
        elif custom.column == self.BIRTHDAY:
          found_birthday = True
        elif custom.column == self.PHOTO_URL:
          found_photourl = True
        elif custom.column == self.EDIT_URL:
          found_editurl = True

    if not found_name and found_birthday and found_photourl and found_editurl:
      print  ("ERROR - Unexpected number of column headers. Should have: %s,"
             " %s, %s, and %s." % (self.NAME, self.BIRTHDAY, self.PHOTO_URL, 
             self.EDIT_URL)) 
      sys.exit(1)

    # For every row in the spreadsheet, grab all the data and either insert
    # a new event into the calendar, or update the existing event

    # Create dict to represent the row data to update edit link back to
    # Spreadsheet
     
    for entry in feed.entry:
      d = {} 
      input_valid = True
      
      for name, custom in entry.custom.iteritems():
        d[custom.column] = custom.text

      month = int(d[self.BIRTHDAY].split("/")[0]) 
      day = int(d[self.BIRTHDAY].split("/")[1])
      
      # Some input checking. Script will allow the insert to continue with
      # a missing name value.
      if d[self.NAME] is None:
        d[self.NAME] = " "
      if d[self.PHOTO_URL] is None:
        input_valid = False
      if d[self.BIRTHDAY] is None:
        input_valid = False
      elif not 1 <= month <= 12 or not 1 <= day <= 31:
        input_valid = False  

      if d[self.EDIT_URL] is None and input_valid:
        event = self._CreateBirthdayWebContentEvent(d[self.NAME], 
            d[self.BIRTHDAY], d[self.PHOTO_URL])
        event = self._InsertBirthdayWebContentEvent(event)
        event = self._AddReminder(event, self.REMINDER)
	print "Added %s's birthday!" % d[self.NAME]
      elif input_valid: # Event already exists
        edit_link = d[self.EDIT_URL]
        event = self._CreateBirthdayWebContentEvent(d[self.NAME], 
            d[self.BIRTHDAY], d[self.PHOTO_URL])          
        event = self.c_client.UpdateEvent(edit_link, event)
        event = self._AddReminder(event, self.REMINDER)
        print "Updated %s's birthday!" % d[self.NAME]
      
      if input_valid:
        d[self.EDIT_URL] = event.GetEditLink().href
        self.s_client.UpdateRow(entry, d)
      else:
        print "Warning - Skipping row, missing valid input." 

def main():
  email = raw_input("Please enter your email: ")
  password = getpass.getpass("Please enter your password: ")
  
  sample = BirthdaySample(email, password)
  sample.Run()


if __name__ == '__main__':
  main()

