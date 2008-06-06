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


import gdata.base.service
import gdata.service
try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import atom
import gdata.base

# Demonstrates queries to the snippets feed and stepping through the results.

gb_client = gdata.base.service.GBaseService()
q = gdata.base.service.BaseQuery()
q.feed = '/base/feeds/snippets'
q['start-index'] = '1'
q['max-results'] = '10'
q.bq = raw_input('Please enter your Google Base query: ')

feed = gb_client.QuerySnippetsFeed(q.ToUri())

while(int(q['start-index']) < 989):
  # Display the titles of the snippets.
  print 'Snippet query results items %s to %s' % (q['start-index'], 
      int(q['start-index'])+10)
  for entry in feed.entry:
    print '  ', entry.title.text

  # Show the next 10 results from the snippets feed when the user presses 
  # enter.
  nothing = raw_input('Press enter to see the next 10 results')
  q['start-index'] = str(int(q['start-index']) + 10)
  feed = gb_client.QuerySnippetsFeed(q.ToUri())

print 'You\'ve reached the upper limit of 1000 items. Goodbye :)'
