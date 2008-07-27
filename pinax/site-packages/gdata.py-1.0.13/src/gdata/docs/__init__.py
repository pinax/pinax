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

"""Contains extensions to Atom objects used with Google Documents."""

__author__ = 'api.jfisher (Jeff Fisher)'

import atom
import gdata


class DocumentListEntry(gdata.GDataEntry):
  """The Google Documents version of an Atom Entry"""
  
  _tag = 'entry'
  _namespace = atom.ATOM_NAMESPACE
  _children = gdata.GDataEntry._children.copy()
  _attributes = gdata.GDataEntry._attributes.copy()


def DocumentListEntryFromString(xml_string):
  """Converts an XML string into a DocumentListEntry object.

  Args:
    xml_string: string The XML describing a Document List feed entry.

  Returns:
    A DocumentListEntry object corresponding to the given XML.
  """
  return atom.CreateClassFromXMLString(DocumentListEntry, xml_string)


class DocumentListFeed(gdata.GDataFeed):
  """A feed containing a list of Google Documents Items"""
  
  _tag = 'feed'
  _namespace = atom.ATOM_NAMESPACE
  _children = gdata.GDataFeed._children.copy()
  _attributes = gdata.GDataFeed._attributes.copy()
  _children['{%s}entry' % atom.ATOM_NAMESPACE] = ('entry', 
                                                  [DocumentListEntry])


def DocumentListFeedFromString(xml_string):
  """Converts an XML string into a DocumentListFeed object.

  Args:
    xml_string: string The XML describing a DocumentList feed.

  Returns:
    A DocumentListFeed object corresponding to the given XML.
  """
  return atom.CreateClassFromXMLString(DocumentListFeed, xml_string)
