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


__author__ = 'api.jscudder@gmail.com (Jeff Scudder)'


import unittest
try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import gdata
from gdata import test_data
import gdata.base


class LabelTest(unittest.TestCase):
  
  def setUp(self):
    self.label = gdata.base.Label()
    
  def testToAndFromString(self):
    self.label.text = 'test label'
    self.assert_(self.label.text == 'test label')
    new_label = gdata.base.LabelFromString(self.label.ToString())
    self.assert_(self.label.text == new_label.text)

    
class ItemTypeTest(unittest.TestCase):
  
  def setUp(self):
    self.item_type = gdata.base.ItemType()
    
  def testToAndFromString(self):
    self.item_type.text = 'product'
    self.item_type.type = 'text'
    self.assert_(self.item_type.text == 'product')
    self.assert_(self.item_type.type == 'text')
    new_item_type = gdata.base.ItemTypeFromString(self.item_type.ToString())
    self.assert_(self.item_type.text == new_item_type.text)
    self.assert_(self.item_type.type == new_item_type.type)


class GBaseItemTest(unittest.TestCase):

  def setUp(self):
    self.item = gdata.base.GBaseItem()
    
  def testToAndFromString(self):
    self.item.label.append(gdata.base.Label(text='my label'))
    self.assert_(self.item.label[0].text == 'my label')
    self.item.item_type = gdata.base.ItemType(text='products')
    self.assert_(self.item.item_type.text == 'products')
    self.item.item_attributes.append(gdata.base.ItemAttribute('extra', text='foo'))
    self.assert_(self.item.item_attributes[0].text == 'foo')
    self.assert_(self.item.item_attributes[0].name == 'extra')
    new_item = gdata.base.GBaseItemFromString(self.item.ToString())
    self.assert_(self.item.label[0].text == new_item.label[0].text)
    self.assert_(self.item.item_type.text == new_item.item_type.text)
    self.assert_(self.item.item_attributes[0].text == 
        new_item.item_attributes[0].text)

  def testCustomItemAttributes(self):
    self.item.AddItemAttribute('test_attrib', 'foo')
    self.assert_(self.item.FindItemAttribute('test_attrib') == 'foo')
    self.item.SetItemAttribute('test_attrib', 'bar')
    self.assert_(self.item.FindItemAttribute('test_attrib') == 'bar')
    self.item.RemoveItemAttribute('test_attrib')
    self.assert_(self.item.FindItemAttribute('test_attrib') is None)

  def testConvertActualData(self):
    feed = gdata.base.GBaseSnippetFeedFromString(test_data.GBASE_FEED)
    for an_entry in feed.entry:
      if an_entry.author[0].email.text == 'anon-szot0wdsq0at@base.google.com':
        for attrib in an_entry.item_attributes:
          if attrib.name == 'payment_notes':
            self.assert_(attrib.text == 
                'PayPal & Bill Me Later credit available online only.')
          if attrib.name == 'condition':
            self.assert_(attrib.text == 'new')
#        self.assert_(an_entry.item_attributes['condition'].text == 'new')

  def testModifyCustomItemAttributes(self):
    self.item.AddItemAttribute('test_attrib', 'foo', value_type='test1')
    self.item.AddItemAttribute('test_attrib', 'bar', value_type='test2')
    self.assertEquals(self.item.item_attributes[0].name, 'test_attrib')
    self.assertEquals(self.item.item_attributes[1].name, 'test_attrib')
    self.assertEquals(self.item.item_attributes[0].text, 'foo')
    self.assertEquals(self.item.item_attributes[1].text, 'bar')

    # Get one of the custom attributes from the item.
    attributes = self.item.GetItemAttributes('test_attrib')
    self.assertEquals(len(attributes), 2)
    self.assertEquals(attributes[0].text, 'foo')
    # Change the contents of the found item attribute.
    attributes[0].text = 'new foo'
    self.assertEquals(attributes[0].text, 'new foo')
    # Make sure that the change is reflected in the item.
    self.assertEquals(self.item.item_attributes[0].text, 'new foo')
    

class GBaseItemFeedTest(unittest.TestCase):

  def setUp(self):
    self.item_feed = gdata.base.GBaseItemFeedFromString(test_data.GBASE_FEED)

  def testToAndFromString(self):
    self.assert_(len(self.item_feed.entry) == 3)
    for an_entry in self.item_feed.entry:
      self.assert_(isinstance(an_entry, gdata.base.GBaseItem))
    new_item_feed = gdata.base.GBaseItemFeedFromString(str(self.item_feed))
    for an_entry in new_item_feed.entry:
      self.assert_(isinstance(an_entry, gdata.base.GBaseItem))
    
    #self.item_feed.label.append(gdata.base.Label(text='my label'))
    #self.assert_(self.item.label[0].text == 'my label')
    #self.item.item_type = gdata.base.ItemType(text='products')
    #self.assert_(self.item.item_type.text == 'products')
    #new_item = gdata.base.GBaseItemFromString(self.item.ToString())
    #self.assert_(self.item.label[0].text == new_item.label[0].text)
    #self.assert_(self.item.item_type.text == new_item.item_type.text)

  def testLinkFinderFindsHtmlLink(self):
    for entry in self.item_feed.entry:
      # All Base entries should have a self link
      self.assert_(entry.GetSelfLink() is not None)
      # All Base items should have an HTML link
      self.assert_(entry.GetHtmlLink() is not None)
      # None of the Base items should have an edit link
      self.assert_(entry.GetEditLink() is None)


class GBaseSnippetFeedTest(unittest.TestCase):

  def setUp(self):
    #self.item_feed = gdata.base.GBaseItemFeed()
    self.snippet_feed = gdata.base.GBaseSnippetFeedFromString(test_data.GBASE_FEED)

  def testToAndFromString(self):
    self.assert_(len(self.snippet_feed.entry) == 3)
    for an_entry in self.snippet_feed.entry:
      self.assert_(isinstance(an_entry, gdata.base.GBaseSnippet))
    new_snippet_feed = gdata.base.GBaseSnippetFeedFromString(str(self.snippet_feed))
    for an_entry in new_snippet_feed.entry:
      self.assert_(isinstance(an_entry, gdata.base.GBaseSnippet))


class ItemAttributeTest(unittest.TestCase):

  def testToAndFromStirng(self):
    attrib = gdata.base.ItemAttribute('price')
    attrib.type = 'float'
    self.assert_(attrib.name == 'price')
    self.assert_(attrib.type == 'float')
    new_attrib = gdata.base.ItemAttributeFromString(str(attrib))
    self.assert_(new_attrib.name == attrib.name)
    self.assert_(new_attrib.type == attrib.type)

  def testClassConvertsActualData(self):
    attrib = gdata.base.ItemAttributeFromString(test_data.TEST_GBASE_ATTRIBUTE)
    self.assert_(attrib.name == 'brand')
    self.assert_(attrib.type == 'text')
    self.assert_(len(attrib.extension_elements) == 0)

    # Test conversion to en ElementTree
    element = attrib._ToElementTree()
    self.assert_(element.tag == gdata.base.GBASE_TEMPLATE % 'brand')


class AttributeTest(unittest.TestCase):

  def testAttributeToAndFromString(self):
    attrib = gdata.base.Attribute()
    attrib.type = 'float'
    attrib.count = '44000'
    attrib.name = 'test attribute'
    attrib.value.append(gdata.base.Value(count='500', text='a value'))
    self.assert_(attrib.type == 'float')
    self.assert_(attrib.count == '44000')
    self.assert_(attrib.name == 'test attribute')
    self.assert_(attrib.value[0].count == '500')
    self.assert_(attrib.value[0].text == 'a value')
    new_attrib = gdata.base.AttributeFromString(str(attrib))
    self.assert_(attrib.type == new_attrib.type)
    self.assert_(attrib.count == new_attrib.count)
    self.assert_(attrib.value[0].count == new_attrib.value[0].count)
    self.assert_(attrib.value[0].text == new_attrib.value[0].text)
    self.assert_(attrib.name == new_attrib.name)


class ValueTest(unittest.TestCase):

  def testValueToAndFromString(self):
    value = gdata.base.Value()
    value.count = '5123'
    value.text = 'super great'
    self.assert_(value.count == '5123')
    self.assert_(value.text == 'super great')
    new_value = gdata.base.ValueFromString(str(value))
    self.assert_(new_value.count == value.count)
    self.assert_(new_value.text == value.text)
    

class AttributeEntryTest(unittest.TestCase):

  def testAttributeEntryToAndFromString(self):
    value = gdata.base.Value(count='500', text='happy')
    attribute = gdata.base.Attribute(count='600', value=[value])
    a_entry = gdata.base.GBaseAttributeEntry(attribute=[attribute])
    self.assert_(a_entry.attribute[0].count == '600')
    self.assert_(a_entry.attribute[0].value[0].count == '500')
    self.assert_(a_entry.attribute[0].value[0].text == 'happy')
    new_entry = gdata.base.GBaseAttributeEntryFromString(str(a_entry))
    self.assert_(new_entry.attribute[0].count == '600')
    self.assert_(new_entry.attribute[0].value[0].count == '500')
    self.assert_(new_entry.attribute[0].value[0].text == 'happy')
    

class GBaseAttributeEntryTest(unittest.TestCase):

  def testAttribteEntryFromExampleData(self):
    entry = gdata.base.GBaseAttributeEntryFromString(
        test_data.GBASE_ATTRIBUTE_ENTRY)
    self.assert_(len(entry.attribute) == 1)
    self.assert_(len(entry.attribute[0].value) == 10)
    self.assert_(entry.attribute[0].name == 'job industry')
    for val in entry.attribute[0].value:
      if val.text == 'it internet':
        self.assert_(val.count == '380772')
      elif val.text == 'healthcare':
        self.assert_(val.count == '261565')
      


class GBaseAttributesFeedTest(unittest.TestCase):

  def testAttributesFeedExampleData(self):
    feed = gdata.base.GBaseAttributesFeedFromString(test_data.GBASE_ATTRIBUTE_FEED)
    self.assert_(len(feed.entry) == 1)
    self.assert_(isinstance(feed.entry[0], gdata.base.GBaseAttributeEntry))

  def testAttributesFeedToAndFromString(self):
    value = gdata.base.Value(count='500', text='happy')
    attribute = gdata.base.Attribute(count='600', value=[value])
    a_entry = gdata.base.GBaseAttributeEntry(attribute=[attribute])
    feed = gdata.base.GBaseAttributesFeed(entry=[a_entry])
    self.assert_(feed.entry[0].attribute[0].count == '600')
    self.assert_(feed.entry[0].attribute[0].value[0].count == '500')
    self.assert_(feed.entry[0].attribute[0].value[0].text == 'happy')
    new_feed = gdata.base.GBaseAttributesFeedFromString(str(feed))
    self.assert_(new_feed.entry[0].attribute[0].count == '600')
    self.assert_(new_feed.entry[0].attribute[0].value[0].count == '500')
    self.assert_(new_feed.entry[0].attribute[0].value[0].text == 'happy')


class GBaseLocalesFeedTest(unittest.TestCase):
  
  def testLocatesFeedWithExampleData(self):
    feed = gdata.base.GBaseLocalesFeedFromString(test_data.GBASE_LOCALES_FEED)
    self.assert_(len(feed.entry) == 3)
    self.assert_(feed.GetSelfLink().href == 
        'http://www.google.com/base/feeds/locales/') 
    for an_entry in feed.entry:
      if an_entry.title.text == 'en_US':
        self.assert_(an_entry.category[0].term == 'en_US')
      self.assert_(an_entry.title.text == an_entry.category[0].term)

  
class GBaseItemTypesFeedAndEntryTest(unittest.TestCase):

  def testItemTypesFeedToAndFromString(self):
    feed = gdata.base.GBaseItemTypesFeed()
    entry = gdata.base.GBaseItemTypeEntry()
    entry.attribute.append(gdata.base.Attribute(name='location', 
        attribute_type='location'))
    entry.item_type = gdata.base.ItemType(text='jobs')
    feed.entry.append(entry)
    self.assert_(len(feed.entry) == 1)
    self.assert_(feed.entry[0].attribute[0].name == 'location')
    new_feed = gdata.base.GBaseItemTypesFeedFromString(str(feed))
    self.assert_(len(new_feed.entry) == 1)
    self.assert_(new_feed.entry[0].attribute[0].name == 'location')

class GBaseImageLinkTest(unittest.TestCase):

  def testImageLinkToAndFromString(self):
    image_link = gdata.base.ImageLink()
    image_link.type = 'url'
    image_link.text = 'example.com'
    thumbnail = gdata.base.Thumbnail()
    thumbnail.width = '60'
    thumbnail.height = '80'
    thumbnail.text = 'example text'
    image_link.thumbnail.append(thumbnail)
    xml = image_link.ToString()    
    parsed = gdata.base.ImageLinkFromString(xml)
    
    self.assert_(parsed.type == image_link.type)
    self.assert_(parsed.text == image_link.text)
    self.assert_(len(parsed.thumbnail) == 1)
    self.assert_(parsed.thumbnail[0].width == thumbnail.width)
    self.assert_(parsed.thumbnail[0].height == thumbnail.height)
    self.assert_(parsed.thumbnail[0].text == thumbnail.text)


class GBaseItemAttributeAccessElement(unittest.TestCase):

  def testItemAttributeAccessAttribute(self):
    item = gdata.base.GBaseItem()
    item.AddItemAttribute('test', '1', value_type='int', access='private')
    private_attribute = item.GetItemAttributes('test')[0]
    self.assert_(private_attribute.access == 'private')
    xml = item.ToString()
    new_item = gdata.base.GBaseItemFromString(xml)
    new_attributes = new_item.GetItemAttributes('test')
    self.assert_(len(new_attributes) == 1)
    #self.assert_(new_attributes[0].access == 'private')
    

if __name__ == '__main__':
  unittest.main()
