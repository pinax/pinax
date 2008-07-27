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


__author__ = 'api.laurabeth@gmail.com (Laura Beth Lincoln)'


try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import gdata.spreadsheet.service
import gdata.service
import atom.service
import gdata.spreadsheet
import atom
import getopt
import sys
import string


class SimpleCRUD:

  def __init__(self, email, password):
    self.gd_client = gdata.spreadsheet.service.SpreadsheetsService()
    self.gd_client.email = email
    self.gd_client.password = password
    self.gd_client.source = 'Spreadsheets GData Sample'
    self.gd_client.ProgrammaticLogin()
    self.curr_key = ''
    self.curr_wksht_id = ''
    self.list_feed = None
    
  def _PromptForSpreadsheet(self):
    # Get the list of spreadsheets
    feed = self.gd_client.GetSpreadsheetsFeed()
    self._PrintFeed(feed)
    input = raw_input('\nSelection: ')
    id_parts = feed.entry[string.atoi(input)].id.text.split('/')
    self.curr_key = id_parts[len(id_parts) - 1]
  
  def _PromptForWorksheet(self):
    # Get the list of worksheets
    feed = self.gd_client.GetWorksheetsFeed(self.curr_key)
    self._PrintFeed(feed)
    input = raw_input('\nSelection: ')
    id_parts = feed.entry[string.atoi(input)].id.text.split('/')
    self.curr_wksht_id = id_parts[len(id_parts) - 1]
  
  def _PromptForCellsAction(self):
    print ('dump\n'
           'update {row} {col} {input_value}\n'
           '\n')
    input = raw_input('Command: ')
    command = input.split(' ', 1)
    if command[0] == 'dump':
      self._CellsGetAction()
    elif command[0] == 'update':
      parsed = command[1].split(' ', 2)
      if len(parsed) == 3:
        self._CellsUpdateAction(parsed[0], parsed[1], parsed[2])
      else:
        self._CellsUpdateAction(parsed[0], parsed[1], '')
    else:
      self._InvalidCommandError(input)
  
  def _PromptForListAction(self):
    print ('dump\n'
           'insert {row_data} (example: insert label=content)\n'
           'update {row_index} {row_data}\n'
           'delete {row_index}\n'
           '\n')
    input = raw_input('Command: ')
    command = input.split(' ' , 1)
    if command[0] == 'dump':
      self._ListGetAction()
    elif command[0] == 'insert':
      self._ListInsertAction(command[1])
    elif command[0] == 'update':
      parsed = command[1].split(' ', 1)
      self._ListUpdateAction(parsed[0], parsed[1])
    elif command[0] == 'delete':
      self._ListDeleteAction(command[1])
    else:
      self._InvalidCommandError(input)
  
  def _CellsGetAction(self):
    # Get the feed of cells
    feed = self.gd_client.GetCellsFeed(self.curr_key, self.curr_wksht_id)
    self._PrintFeed(feed)
    
  def _CellsUpdateAction(self, row, col, inputValue):
    entry = self.gd_client.UpdateCell(row=row, col=col, inputValue=inputValue, 
        key=self.curr_key, wksht_id=self.curr_wksht_id)
    if isinstance(entry, gdata.spreadsheet.SpreadsheetsCell):
      print 'Updated!'
        
  def _ListGetAction(self):
    # Get the list feed
    self.list_feed = self.gd_client.GetListFeed(self.curr_key, self.curr_wksht_id)
    self._PrintFeed(self.list_feed)
    
  def _ListInsertAction(self, row_data):
    entry = self.gd_client.InsertRow(self._StringToDictionary(row_data), 
        self.curr_key, self.curr_wksht_id)
    if isinstance(entry, gdata.spreadsheet.SpreadsheetsList):
      print 'Inserted!'
        
  def _ListUpdateAction(self, index, row_data):
    self.list_feed = self.gd_client.GetListFeed(self.curr_key, self.curr_wksht_id)
    entry = self.gd_client.UpdateRow(
        self.list_feed.entry[string.atoi(index)], 
        self._StringToDictionary(row_data))
    if isinstance(entry, gdata.spreadsheet.SpreadsheetsList):
      print 'Updated!'
  
  def _ListDeleteAction(self, index):
    self.list_feed = self.gd_client.GetListFeed(self.curr_key, self.curr_wksht_id)
    self.gd_client.DeleteRow(self.list_feed.entry[string.atoi(index)])
    print 'Deleted!'
    
  def _StringToDictionary(self, row_data):
    dict = {}
    for param in row_data.split():
      temp = param.split('=')
      dict[temp[0]] = temp[1]
    return dict
  
  def _PrintFeed(self, feed):
    for i, entry in enumerate(feed.entry):
      if isinstance(feed, gdata.spreadsheet.SpreadsheetsCellsFeed):
        print '%s %s\n' % (entry.title.text, entry.content.text)
      elif isinstance(feed, gdata.spreadsheet.SpreadsheetsListFeed):
        #print '%s %s %s\n' % (i, entry.title.text.encode('UTF-8'), entry.content.text.encode('UTF-8'))
        print '%s %s %s\n' % (i, entry.title.text, entry.content.text)
      else:
        print '%s %s\n' % (i, entry.title.text)
        
  def _InvalidCommandError(self, input):
    print 'Invalid input: %s\n' % (input)
    
  def Run(self):
    self._PromptForSpreadsheet()
    self._PromptForWorksheet()
    input = raw_input('cells or list? ')
    if input == 'cells':
      while True:
        self._PromptForCellsAction()
    elif input == 'list':
      while True:
        self._PromptForListAction()


def main():
  # parse command line options
  try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["user=", "pw="])
  except getopt.error, msg:
    print 'python spreadsheetExample.py --user [username] --pw [password] '
    sys.exit(2)
  
  user = ''
  pw = ''
  key = ''
  # Process options
  for o, a in opts:
    if o == "--user":
      user = a
    elif o == "--pw":
      pw = a

  if user == '' or pw == '':
    print 'python spreadsheetExample.py --user [username] --pw [password] '
    sys.exit(2)
        
  sample = SimpleCRUD(user, pw)
  sample.Run()


if __name__ == '__main__':
  main()
