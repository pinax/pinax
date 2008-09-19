#!/usr/bin/python
# -*-*- encoding: utf-8 -*-*-
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


import sys
import unittest
try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import atom
from gdata import test_data


class AuthorTest(unittest.TestCase):
  
  def setUp(self):
    self.author = atom.Author()
    
  def testEmptyAuthorShouldHaveEmptyExtensionsList(self):
    self.assert_(isinstance(self.author.extension_elements, list))
    self.assert_(len(self.author.extension_elements) == 0)
    
  def testNormalAuthorShouldHaveNoExtensionElements(self):
    self.author.name = atom.Name(text='Jeff Scudder')
    self.assert_(self.author.name.text == 'Jeff Scudder')
    self.assert_(len(self.author.extension_elements) == 0)
    new_author = atom.AuthorFromString(self.author.ToString())
    self.assert_(len(self.author.extension_elements) == 0)
    
    self.author.extension_elements.append(atom.ExtensionElement(
        'foo', text='bar'))
    self.assert_(len(self.author.extension_elements) == 1)
    self.assert_(self.author.name.text == 'Jeff Scudder')
    new_author = atom.AuthorFromString(self.author.ToString())
    self.assert_(len(self.author.extension_elements) == 1)
    self.assert_(new_author.name.text == 'Jeff Scudder')

  def testEmptyAuthorToAndFromStringShouldMatch(self):
    string_from_author = self.author.ToString()
    new_author = atom.AuthorFromString(string_from_author)
    string_from_new_author = new_author.ToString()
    self.assert_(string_from_author == string_from_new_author)
    
  def testAuthorWithNameToAndFromStringShouldMatch(self):
    self.author.name = atom.Name()
    self.author.name.text = 'Jeff Scudder'
    string_from_author = self.author.ToString()
    new_author = atom.AuthorFromString(string_from_author)
    string_from_new_author = new_author.ToString()
    self.assert_(string_from_author == string_from_new_author)
    self.assert_(self.author.name.text == new_author.name.text)
  
  def testExtensionElements(self):
    self.author.extension_attributes['foo1'] = 'bar'
    self.author.extension_attributes['foo2'] = 'rab'
    self.assert_(self.author.extension_attributes['foo1'] == 'bar')
    self.assert_(self.author.extension_attributes['foo2'] == 'rab')
    new_author = atom.AuthorFromString(self.author.ToString())
    self.assert_(new_author.extension_attributes['foo1'] == 'bar')
    self.assert_(new_author.extension_attributes['foo2'] == 'rab')
    
  def testConvertFullAuthorToAndFromString(self):
    author = atom.AuthorFromString(test_data.TEST_AUTHOR)
    self.assert_(author.name.text == 'John Doe')
    self.assert_(author.email.text == 'johndoes@someemailadress.com')
    self.assert_(author.uri.text == 'http://www.google.com')
    
    
class EmailTest(unittest.TestCase):
  
  def setUp(self):
    self.email = atom.Email()
    
  def testEmailToAndFromString(self):
    self.email.text = 'This is a test'
    new_email = atom.EmailFromString(self.email.ToString())
    self.assert_(self.email.text == new_email.text)
    self.assert_(self.email.extension_elements == 
        new_email.extension_elements)
    
  
class NameTest(unittest.TestCase):

  def setUp(self):
    self.name = atom.Name()
    
  def testEmptyNameToAndFromStringShouldMatch(self):
    string_from_name = self.name.ToString()
    new_name = atom.NameFromString(string_from_name)
    string_from_new_name = new_name.ToString()
    self.assert_(string_from_name == string_from_new_name)
    
  def testText(self):
    self.assert_(self.name.text is None)
    self.name.text = 'Jeff Scudder'
    self.assert_(self.name.text == 'Jeff Scudder')
    new_name = atom.NameFromString(self.name.ToString())
    self.assert_(new_name.text == self.name.text)
    
  def testExtensionElements(self):
    self.name.extension_attributes['foo'] = 'bar'
    self.assert_(self.name.extension_attributes['foo'] == 'bar')
    new_name = atom.NameFromString(self.name.ToString())
    self.assert_(new_name.extension_attributes['foo'] == 'bar')
    
    
class ExtensionElementTest(unittest.TestCase):
  
  def setUp(self):
    self.ee = atom.ExtensionElement('foo')
    
  def testEmptyEEShouldProduceEmptyString(self):
    pass
    
  def testEEParsesTreeCorrectly(self):
    deep_tree = atom.ExtensionElementFromString(test_data.EXTENSION_TREE)
    self.assert_(deep_tree.tag == 'feed')
    self.assert_(deep_tree.namespace == 'http://www.w3.org/2005/Atom')
    self.assert_(deep_tree.children[0].tag == 'author')
    self.assert_(deep_tree.children[0].namespace == 'http://www.google.com')
    self.assert_(deep_tree.children[0].children[0].tag == 'name')
    self.assert_(deep_tree.children[0].children[0].namespace == 
        'http://www.google.com')
    self.assert_(deep_tree.children[0].children[0].text.strip() == 'John Doe')
    self.assert_(deep_tree.children[0].children[0].children[0].text.strip() ==
        'Bar')
    foo = deep_tree.children[0].children[0].children[0]
    self.assert_(foo.tag == 'foo')
    self.assert_(foo.namespace == 'http://www.google.com')
    self.assert_(foo.attributes['up'] == 'down')
    self.assert_(foo.attributes['yes'] == 'no')
    self.assert_(foo.children == [])
  
  def testEEToAndFromStringShouldMatch(self):
    string_from_ee = self.ee.ToString()
    new_ee = atom.ExtensionElementFromString(string_from_ee)
    string_from_new_ee = new_ee.ToString()
    self.assert_(string_from_ee == string_from_new_ee)
    
    deep_tree = atom.ExtensionElementFromString(test_data.EXTENSION_TREE)    
    string_from_deep_tree = deep_tree.ToString()
    new_deep_tree = atom.ExtensionElementFromString(string_from_deep_tree)
    string_from_new_deep_tree = new_deep_tree.ToString()
    self.assert_(string_from_deep_tree == string_from_new_deep_tree)
    
    
class LinkTest(unittest.TestCase):
  
  def setUp(self):
    self.link = atom.Link()
    
  def testLinkToAndFromString(self):
    self.link.href = 'test href'
    self.link.hreflang = 'english'
    self.link.type = 'text/html'
    self.link.extension_attributes['foo'] = 'bar'
    self.assert_(self.link.href == 'test href')
    self.assert_(self.link.hreflang == 'english')
    self.assert_(self.link.type == 'text/html')
    self.assert_(self.link.extension_attributes['foo'] == 'bar')
    new_link = atom.LinkFromString(self.link.ToString())
    self.assert_(self.link.href == new_link.href)
    self.assert_(self.link.type == new_link.type)
    self.assert_(self.link.hreflang == new_link.hreflang)
    self.assert_(self.link.extension_attributes['foo'] == 
        new_link.extension_attributes['foo'])

  def testLinkType(self):
    test_link = atom.Link(link_type='text/html')
    self.assert_(test_link.type == 'text/html')


class GeneratorTest(unittest.TestCase):

  def setUp(self):
    self.generator = atom.Generator()

  def testGeneratorToAndFromString(self):
    self.generator.uri = 'www.google.com'
    self.generator.version = '1.0'
    self.generator.extension_attributes['foo'] = 'bar'
    self.assert_(self.generator.uri == 'www.google.com')
    self.assert_(self.generator.version == '1.0')
    self.assert_(self.generator.extension_attributes['foo'] == 'bar')
    new_generator = atom.GeneratorFromString(self.generator.ToString())
    self.assert_(self.generator.uri == new_generator.uri)
    self.assert_(self.generator.version == new_generator.version)
    self.assert_(self.generator.extension_attributes['foo'] ==
        new_generator.extension_attributes['foo'])


class TitleTest(unittest.TestCase):

  def setUp(self):
    self.title = atom.Title()

  def testTitleToAndFromString(self):
    self.title.type = 'text'
    self.title.text = 'Less: &lt;'
    self.assert_(self.title.type == 'text')
    self.assert_(self.title.text == 'Less: &lt;')
    new_title = atom.TitleFromString(self.title.ToString())
    self.assert_(self.title.type == new_title.type)
    self.assert_(self.title.text == new_title.text)


class SubtitleTest(unittest.TestCase):

  def setUp(self):
    self.subtitle = atom.Subtitle()

  def testTitleToAndFromString(self):
    self.subtitle.type = 'text'
    self.subtitle.text = 'sub & title'
    self.assert_(self.subtitle.type == 'text')
    self.assert_(self.subtitle.text == 'sub & title')
    new_subtitle = atom.SubtitleFromString(self.subtitle.ToString())
    self.assert_(self.subtitle.type == new_subtitle.type)
    self.assert_(self.subtitle.text == new_subtitle.text)



class SummaryTest(unittest.TestCase):

  def setUp(self):
    self.summary = atom.Summary()

  def testTitleToAndFromString(self):
    self.summary.type = 'text'
    self.summary.text = 'Less: &lt;'
    self.assert_(self.summary.type == 'text')
    self.assert_(self.summary.text == 'Less: &lt;')
    new_summary = atom.SummaryFromString(self.summary.ToString())
    self.assert_(self.summary.type == new_summary.type)
    self.assert_(self.summary.text == new_summary.text)


class CategoryTest(unittest.TestCase):

  def setUp(self):
    self.category = atom.Category()

  def testCategoryToAndFromString(self):
    self.category.term = 'x'
    self.category.scheme = 'y'
    self.category.label = 'z'
    self.assert_(self.category.term == 'x')
    self.assert_(self.category.scheme == 'y')
    self.assert_(self.category.label == 'z')
    new_category = atom.CategoryFromString(self.category.ToString())
    self.assert_(self.category.term == new_category.term)
    self.assert_(self.category.scheme == new_category.scheme)
    self.assert_(self.category.label == new_category.label)


class ContributorTest(unittest.TestCase):

  def setUp(self):
    self.contributor = atom.Contributor()

  def testContributorToAndFromString(self):
    self.contributor.name = atom.Name(text='J Scud')
    self.contributor.email = atom.Email(text='nobody@nowhere')
    self.contributor.uri = atom.Uri(text='http://www.google.com')
    self.assert_(self.contributor.name.text == 'J Scud')
    self.assert_(self.contributor.email.text == 'nobody@nowhere')
    self.assert_(self.contributor.uri.text == 'http://www.google.com')
    new_contributor = atom.ContributorFromString(self.contributor.ToString())
    self.assert_(self.contributor.name.text == new_contributor.name.text)
    self.assert_(self.contributor.email.text == new_contributor.email.text)
    self.assert_(self.contributor.uri.text == new_contributor.uri.text)


class IdTest(unittest.TestCase):

  def setUp(self):
    self.my_id = atom.Id()

  def testIdToAndFromString(self):
    self.my_id.text = 'my nifty id'
    self.assert_(self.my_id.text == 'my nifty id')
    new_id = atom.IdFromString(self.my_id.ToString())
    self.assert_(self.my_id.text == new_id.text)


class IconTest(unittest.TestCase):

  def setUp(self):
    self.icon = atom.Icon()

  def testIconToAndFromString(self):
    self.icon.text = 'my picture'
    self.assert_(self.icon.text == 'my picture')
    new_icon = atom.IconFromString(str(self.icon))
    self.assert_(self.icon.text == new_icon.text)


class LogoTest(unittest.TestCase):

  def setUp(self):
    self.logo = atom.Logo()

  def testLogoToAndFromString(self):
    self.logo.text = 'my logo'
    self.assert_(self.logo.text == 'my logo')
    new_logo = atom.LogoFromString(self.logo.ToString())
    self.assert_(self.logo.text == new_logo.text)


class RightsTest(unittest.TestCase):

  def setUp(self):
    self.rights = atom.Rights()

  def testContributorToAndFromString(self):
    self.rights.text = 'you have the right to remain silent'
    self.rights.type = 'text'
    self.assert_(self.rights.text == 'you have the right to remain silent')
    self.assert_(self.rights.type == 'text')
    new_rights = atom.RightsFromString(self.rights.ToString())
    self.assert_(self.rights.text == new_rights.text)
    self.assert_(self.rights.type == new_rights.type)


class UpdatedTest(unittest.TestCase):

  def setUp(self):
    self.updated = atom.Updated()

  def testUpdatedToAndFromString(self):
    self.updated.text = 'my time'
    self.assert_(self.updated.text == 'my time')
    new_updated = atom.UpdatedFromString(self.updated.ToString())
    self.assert_(self.updated.text == new_updated.text)


class PublishedTest(unittest.TestCase):

  def setUp(self):
    self.published = atom.Published()

  def testPublishedToAndFromString(self):
    self.published.text = 'pub time'
    self.assert_(self.published.text == 'pub time')
    new_published = atom.PublishedFromString(self.published.ToString())
    self.assert_(self.published.text == new_published.text)


class FeedEntryParentTest(unittest.TestCase):
  """The test accesses hidden methods in atom.FeedEntryParent"""

  def testConvertToAndFromElementTree(self):
    # Use entry because FeedEntryParent doesn't have a tag or namespace.
    original = atom.Entry()
    copy = atom.FeedEntryParent()
 
    original.author.append(atom.Author(name=atom.Name(text='J Scud')))
    self.assert_(original.author[0].name.text == 'J Scud')
    self.assert_(copy.author == [])

    original.id = atom.Id(text='test id')
    self.assert_(original.id.text == 'test id')
    self.assert_(copy.id is None)

    copy._HarvestElementTree(original._ToElementTree())
    self.assert_(original.author[0].name.text == copy.author[0].name.text)
    self.assert_(original.id.text == copy.id.text)


class EntryTest(unittest.TestCase):

  def testConvertToAndFromString(self):
    entry = atom.Entry()
    entry.author.append(atom.Author(name=atom.Name(text='js')))
    entry.title = atom.Title(text='my test entry')
    self.assert_(entry.author[0].name.text == 'js')
    self.assert_(entry.title.text == 'my test entry')
    new_entry = atom.EntryFromString(entry.ToString())
    self.assert_(new_entry.author[0].name.text == 'js')
    self.assert_(new_entry.title.text == 'my test entry')

  def testEntryCorrectlyConvertsActualData(self):
    entry = atom.EntryFromString(test_data.XML_ENTRY_1)
    self.assert_(entry.category[0].scheme == 
        'http://base.google.com/categories/itemtypes')
    self.assert_(entry.category[0].term == 'products')
    self.assert_(entry.id.text == '    http://www.google.com/test/id/url   ')
    self.assert_(entry.title.text == 'Testing 2000 series laptop')
    self.assert_(entry.title.type == 'text')
    self.assert_(entry.content.type == 'xhtml')
    #TODO check all other values for the test entry

  def testAppControl(self):
    entry = atom.EntryFromString(test_data.TEST_BASE_ENTRY)
    self.assertEquals(entry.control.draft.text, 'yes')
    self.assertEquals(len(entry.control.extension_elements), 1)
    self.assertEquals(entry.control.extension_elements[0].tag, 'disapproved')


class ControlTest(unittest.TestCase):

  def testConvertToAndFromString(self):
    control = atom.Control()
    control.text = 'some text'
    control.draft = atom.Draft(text='yes')
    self.assertEquals(control.draft.text, 'yes')
    self.assertEquals(control.text, 'some text')
    self.assertEquals(isinstance(control.draft, atom.Draft), True)
    new_control = atom.ControlFromString(str(control))
    self.assertEquals(control.draft.text, new_control.draft.text)
    self.assertEquals(control.text, new_control.text)
    self.assertEquals(isinstance(new_control.draft, atom.Draft), True)


class DraftTest(unittest.TestCase):

  def testConvertToAndFromString(self):
    draft = atom.Draft()
    draft.text = 'maybe'
    draft.extension_attributes['foo'] = 'bar'
    self.assertEquals(draft.text, 'maybe')
    self.assertEquals(draft.extension_attributes['foo'], 'bar')
    new_draft = atom.DraftFromString(str(draft))
    self.assertEquals(draft.text, new_draft.text)
    self.assertEquals(draft.extension_attributes['foo'], 
        new_draft.extension_attributes['foo'])
    
    
    
class SourceTest(unittest.TestCase):

  def testConvertToAndFromString(self):
    source = atom.Source()
    source.author.append(atom.Author(name=atom.Name(text='js')))
    source.title = atom.Title(text='my test source')
    source.generator = atom.Generator(text='gen')
    self.assert_(source.author[0].name.text == 'js')
    self.assert_(source.title.text == 'my test source')
    self.assert_(source.generator.text == 'gen')
    new_source = atom.SourceFromString(source.ToString())
    self.assert_(new_source.author[0].name.text == 'js')
    self.assert_(new_source.title.text == 'my test source')
    self.assert_(new_source.generator.text == 'gen')


class FeedTest(unittest.TestCase):

  def testConvertToAndFromString(self):
    feed = atom.Feed()
    feed.author.append(atom.Author(name=atom.Name(text='js')))
    feed.title = atom.Title(text='my test source')
    feed.generator = atom.Generator(text='gen')
    feed.entry.append(atom.Entry(author=[atom.Author(name=atom.Name(text='entry author'))]))
    self.assert_(feed.author[0].name.text == 'js')
    self.assert_(feed.title.text == 'my test source')
    self.assert_(feed.generator.text == 'gen')
    self.assert_(feed.entry[0].author[0].name.text == 'entry author')
    new_feed = atom.FeedFromString(feed.ToString())
    self.assert_(new_feed.author[0].name.text == 'js')
    self.assert_(new_feed.title.text == 'my test source')
    self.assert_(new_feed.generator.text == 'gen')    
    self.assert_(new_feed.entry[0].author[0].name.text == 'entry author')


class ContentEntryParentTest(unittest.TestCase):
  """The test accesses hidden methods in atom.FeedEntryParent"""

  def setUp(self):
    self.content = atom.Content()

  def testConvertToAndFromElementTree(self):
    self.content.text = 'my content'
    self.content.type = 'text'
    self.content.src = 'my source'
    self.assert_(self.content.text == 'my content')
    self.assert_(self.content.type == 'text')
    self.assert_(self.content.src == 'my source')
    new_content = atom.ContentFromString(self.content.ToString())
    self.assert_(self.content.text == new_content.text)
    self.assert_(self.content.type == new_content.type)
    self.assert_(self.content.src == new_content.src)

  def testContentConstructorSetsSrc(self):
    new_content = atom.Content(src='abcd')
    self.assertEquals(new_content.src, 'abcd')


class PreserveUnkownElementTest(unittest.TestCase):
  """Tests correct preservation of XML elements which are non Atom"""
  
  def setUp(self):
    self.feed = atom.FeedFromString(test_data.GBASE_ATTRIBUTE_FEED)

  def testCaptureOpenSearchElements(self):
    self.assertEquals(self.feed.FindExtensions('totalResults')[0].tag,
        'totalResults')
    self.assertEquals(self.feed.FindExtensions('totalResults')[0].namespace,
        'http://a9.com/-/spec/opensearchrss/1.0/')
    open_search_extensions = self.feed.FindExtensions(
        namespace='http://a9.com/-/spec/opensearchrss/1.0/')
    self.assertEquals(len(open_search_extensions), 3)
    for element in open_search_extensions:
      self.assertEquals(element.namespace, 
          'http://a9.com/-/spec/opensearchrss/1.0/')

  def testCaptureMetaElements(self):
    meta_elements = self.feed.entry[0].FindExtensions(
        namespace='http://base.google.com/ns-metadata/1.0')
    self.assertEquals(len(meta_elements), 1)
    self.assertEquals(meta_elements[0].attributes['count'], '4416629')
    self.assertEquals(len(meta_elements[0].children), 10)

  def testCaptureMetaChildElements(self):
    meta_elements = self.feed.entry[0].FindExtensions(
        namespace='http://base.google.com/ns-metadata/1.0')
    meta_children = meta_elements[0].FindChildren(
        namespace='http://base.google.com/ns-metadata/1.0')
    self.assertEquals(len(meta_children), 10)
    for child in meta_children:
      self.assertEquals(child.tag, 'value')


class LinkFinderTest(unittest.TestCase):
  
  def setUp(self):
    self.entry = atom.EntryFromString(test_data.XML_ENTRY_1)

  def testLinkFinderGetsLicenseLink(self):
    self.assertEquals(isinstance(self.entry.GetLicenseLink(), atom.Link), 
                      True)
    self.assertEquals(self.entry.GetLicenseLink().href,
        'http://creativecommons.org/licenses/by-nc/2.5/rdf')
    self.assertEquals(self.entry.GetLicenseLink().rel, 'license')

  def testLinkFinderGetsAlternateLink(self):
    self.assertEquals(isinstance(self.entry.GetAlternateLink(), atom.Link), 
                      True)
    self.assertEquals(self.entry.GetAlternateLink().href,
        'http://www.provider-host.com/123456789')
    self.assertEquals(self.entry.GetAlternateLink().rel, 'alternate')


class AtomBaseTest(unittest.TestCase):

   def testAtomBaseConvertsExtensions(self):
     # Using Id because it adds no additional members.
     atom_base = atom.Id()
     extension_child = atom.ExtensionElement('foo', namespace='http://ns0.com')
     extension_grandchild = atom.ExtensionElement('bar', namespace='http://ns0.com')
     extension_child.children.append(extension_grandchild)
     atom_base.extension_elements.append(extension_child)
     self.assertEquals(len(atom_base.extension_elements), 1)
     self.assertEquals(len(atom_base.extension_elements[0].children), 1)
     self.assertEquals(atom_base.extension_elements[0].tag, 'foo')
     self.assertEquals(atom_base.extension_elements[0].children[0].tag, 'bar')
     
     element_tree = atom_base._ToElementTree()
     self.assert_(element_tree.find('{http://ns0.com}foo') is not None)
     self.assert_(element_tree.find('{http://ns0.com}foo').find('{http://ns0.com}bar') is not None)


class UtfParsingTest(unittest.TestCase):
  
  def setUp(self):
    self.test_xml = u"""<?xml version="1.0" encoding="utf-8"?><entry xmlns='http://www.w3.org/2005/Atom'>
  <id>http://www.google.com/test/id/url</id>
  <title type='\u03B1\u03BB\u03C6\u03B1'>\u03B1\u03BB\u03C6\u03B1</title>
</entry>"""

  def testMemberStringEncoding(self):
    atom_entry = atom.EntryFromString(self.test_xml)
    self.assert_(atom_entry.title.type == u'\u03B1\u03BB\u03C6\u03B1'.encode('utf-8'))
    self.assert_(atom_entry.title.text == u'\u03B1\u03BB\u03C6\u03B1'.encode('utf-8'))

  def testConvertExampleXML(self):
    try:
      entry = atom.CreateClassFromXMLString(atom.Entry, test_data.GBASE_STRING_ENCODING_ENTRY)
    except UnicodeDecodeError:
      self.fail('Error when converting XML')
    
  
if __name__ == '__main__':
  unittest.main()
