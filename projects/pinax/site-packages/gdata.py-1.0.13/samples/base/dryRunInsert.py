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
import getpass

# Demonstrates item insertion with a dry run insert operation. The item will
# NOT be added to Google Base.

gb_client = gdata.base.service.GBaseService()
gb_client.email = raw_input('Please enter your username: ')
gb_client.password = getpass.getpass()

print 'Logging in'
gb_client.ProgrammaticLogin()

# Create a test item which will be used in a dry run insert
item = gdata.base.GBaseItem()
item.author.append(atom.Author(name=atom.Name(text='Mr. Smith')))
item.title = atom.Title(text='He Jingxian\'s chicken')
item.link.append(atom.Link(rel='alternate', link_type='text/html',
    href='http://www.host.com/123456jsh9'))
item.label.append(gdata.base.Label(text='kung pao chicken'))
item.label.append(gdata.base.Label(text='chinese cuisine'))
item.label.append(gdata.base.Label(text='testrecipes'))
item.item_type = gdata.base.ItemType(text='recipes')
item.AddItemAttribute(name='cooking_time', value_type='intUnit', value='30 minutes')
item.AddItemAttribute(name='main_ingredient', value='chicken')
item.AddItemAttribute(name='main_ingredient', value='chili')

# Make an insert request with the dry run flag set so that the item will not
# actually be created.
result = gb_client.InsertItem(item, url_params={'dry-run': 'true'})

# Send the XML from the server to standard out.
print 'Here\'s the XML from the server\'s simulated insert'
print str(result)

print 'Done'
