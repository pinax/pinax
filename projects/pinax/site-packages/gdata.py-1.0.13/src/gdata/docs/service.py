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

"""DocsService extends the GDataService to streamline Google Documents
  operations.

  DocsService: Provides methods to query feeds and manipulate items.
                    Extends GDataService.

  DocumentQuery: Queries a Google Document list feed.
"""


__author__ = 'api.jfisher (Jeff Fisher)'


import urllib
import atom
import gdata.service
import gdata.docs


# XML Namespaces used in Google Documents entities.
DATA_KIND_SCHEME = 'http://schemas.google.com/g/2005#kind'
DOCUMENT_KIND_TERM = 'http://schemas.google.com/docs/2007#document'
SPREADSHEET_KIND_TERM = 'http://schemas.google.com/docs/2007#spreadsheet'
PRESENTATION_KIND_TERM = 'http://schemas.google.com/docs/2007#presentation'
# File extensions of documents that are permitted to be uploaded.
SUPPORTED_FILETYPES = {
  'CSV': 'text/csv',
  'TSV': 'text/tab-separated-values',
  'TAB': 'text/tab-separated-values',
  'DOC': 'application/msword',
  'ODS': 'application/x-vnd.oasis.opendocument.spreadsheet',
  'ODT': 'application/vnd.oasis.opendocument.text',
  'RTF': 'application/rtf',
  'SXW': 'application/vnd.sun.xml.writer',
  'TXT': 'text/plain',
  'XLS': 'application/vnd.ms-excel',
  'PPT': 'application/vnd.ms-powerpoint',
  'PPS': 'application/vnd.ms-powerpoint',
  'HTM': 'text/html',
  'HTML' : 'text/html'}


class DocsService(gdata.service.GDataService):

  """Client extension for the Google Documents service Document List feed."""

  def __init__(self, email=None, password=None, source=None,
      server='docs.google.com', additional_headers=None):
    """Constructor for the DocsService.

    Args:
      email: string (optional) The e-mail address of the account to use for
             authentication.
      password: string (optional) The password of the account to use for
                authentication.
      source: string (optional) The name of the user's application.
      server: string (optional) The server the feed is hosted on.
      additional_headers: dict (optional) Any additional HTTP headers to be
                          transmitted to the service in the form of key-value
                          pairs.

    Yields:
      A DocsService object used to communicate with the Google Documents
      service.
    """
    gdata.service.GDataService.__init__(self, email=email, password=password,
                                        service='writely', source=source,
                                        server=server,
                                        additional_headers=additional_headers)

  def Query(self, uri, converter=gdata.docs.DocumentListFeedFromString):
    """Queries the Document List feed and returns the resulting feed of
       entries.

    Args:
      uri: string The full URI to be queried. This can contain query
           parameters, a hostname, or simply the relative path to a Document
           List feed. The DocumentQuery object is useful when constructing
           query parameters.
      converter: func (optional) A function which will be executed on the
                 retrieved item, generally to render it into a Python object.
                 By default the DocumentListFeedFromString function is used to
                 return a DocumentListFeed object. This is because most feed
                 queries will result in a feed and not a single entry.
    """
    return self.Get(uri, converter=converter)

  def QueryDocumentListFeed(self, uri):
    """Retrieves a DocumentListFeed by retrieving a URI based off the Document
       List feed, including any query parameters. A DocumentQuery object can
       be used to construct these parameters.

    Args:
      uri: string The URI of the feed being retrieved possibly with query
           parameters.

    Returns:
      A DocumentListFeed object representing the feed returned by the server.
    """
    return self.Get(uri, converter=gdata.docs.DocumentListFeedFromString)

  def GetDocumentListEntry(self, uri):
    """Retrieves a particular DocumentListEntry by its unique URI.

    Args:
      uri: string The unique URI of an entry in a Document List feed.

    Returns:
      A DocumentListEntry object representing the retrieved entry.
      """
    return self.Get(uri, converter=gdata.docs.DocumentListEntryFromString)

  def GetDocumentListFeed(self):
    """Retrieves a feed containing all of a user's documents."""
    q = gdata.docs.service.DocumentQuery();
    return self.QueryDocumentListFeed(q.ToUri())

  def UploadPresentation(self, media_source, title):
    """Uploads a presentation inside of a MediaSource object to the Document
       List feed with the given title.

    Args:
      media_source: MediaSource The MediaSource object containing a
          presentation file to be uploaded.
      title: string The title of the presentation on the server after being
          uploaded.

    Returns:
      A GDataEntry containing information about the presentation created on the
      Google Documents service.
    """
    category = atom.Category(scheme=DATA_KIND_SCHEME,
        term=PRESENTATION_KIND_TERM)
    return self._UploadFile(media_source, title, category)

  def UploadSpreadsheet(self, media_source, title):
    """Uploads a spreadsheet inside of a MediaSource object to the Document
       List feed with the given title.

    Args:
      media_source: MediaSource The MediaSource object containing a spreadsheet
                    file to be uploaded.
      title: string The title of the spreadsheet on the server after being
             uploaded.

    Returns:
      A GDataEntry containing information about the spreadsheet created on the
      Google Documents service.
    """
    category = atom.Category(scheme=DATA_KIND_SCHEME,
        term=SPREADSHEET_KIND_TERM)
    return self._UploadFile(media_source, title, category)

  def UploadDocument(self, media_source, title):
    """Uploads a document inside of a MediaSource object to the Document List
       feed with the given title.

    Args:
      media_source: MediaSource The gdata.MediaSource object containing a
                    document file to be uploaded.
      title: string The title of the document on the server after being
             uploaded.

    Returns:
      A GDataEntry containing information about the document created on the
      Google Documents service.
    """
    category = atom.Category(scheme=DATA_KIND_SCHEME,
        term=DOCUMENT_KIND_TERM)
    return self._UploadFile(media_source, title, category)

  def _UploadFile(self, media_source, title, category):
    """Uploads a file to the Document List feed.
    
    Args:
      media_source: A gdata.MediaSource object containing the file to be
                    uploaded.
      title: string The title of the document on the server after being
             uploaded.
      category: An atom.Category object specifying the appropriate document
                type
    Returns:
      A GDataEntry containing information about the document created on
      the Google Documents service.
     """
    media_entry = gdata.GDataEntry()
    media_entry.title = atom.Title(text=title)
    media_entry.category.append(category)
    media_entry = self.Post(media_entry, '/feeds/documents/private/full',
        media_source = media_source,
        extra_headers = {'Slug' : media_source.file_name })

    return media_entry


class DocumentQuery(gdata.service.Query):
 
  """Object used to construct a URI to query the Google Document List feed"""

  def __init__(self, feed='/feeds/documents', visibility='private',
      projection='full', text_query=None, params=None,
      categories=None):
    """Constructor for Document List Query

    Args:
      feed: string (optional) The path for the feed. (e.g. '/feeds/documents')
      visibility: string (optional) The visibility chosen for the current feed.
      projection: string (optional) The projection chosen for the current feed.
      text_query: string (optional) The contents of the q query parameter. This
                  string is URL escaped upon conversion to a URI.
      params: dict (optional) Parameter value string pairs which become URL
              params when translated to a URI. These parameters are added to
              the query's items.
      categories: list (optional) List of category strings which should be
              included as query categories. See gdata.service.Query for
              additional documentation.

    Yields:
      A DocumentQuery object used to construct a URI based on the Document
      List feed.
    """
    self.visibility = visibility
    self.projection = projection
    gdata.service.Query.__init__(self, feed, text_query, params, categories)

  def ToUri(self):
    """Generates a URI from the query parameters set in the object.

    Returns:
      A string containing the URI used to retrieve entries from the Document
      List feed.
    """
    old_feed = self.feed
    self.feed = '/'.join([old_feed, self.visibility, self.projection])
    new_feed = gdata.service.Query.ToUri(self)
    self.feed = old_feed
    return new_feed

  def AddNamedFolder(self, email, folder_name):
    """Adds a named folder category, qualified by a schema.

    This function lets you query for documents that are contained inside a
    named folder without fear of collision with other categories.

    Args:
      email: string The email of the user who owns the folder.
      folder_name: string The name of the folder.

      Returns:
        The string of the category that was added to the object.
    """

    category = '{http://schemas.google.com/docs/2007/folders/'
    category += email + '}' + folder_name

    self.categories.append(category)

    return category

  def RemoveNamedFolder(self, email, folder_name):
    """Removes a named folder category, qualified by a schema.

    Args:
      email: string The email of the user who owns the folder.
      folder_name: string The name of the folder.

      Returns:
        The string of the category that was removed to the object.
    """

    category = '{http://schemas.google.com/docs/2007/folders/'
    category += email + '}' + folder_name

    self.categories.remove(category)

    return category
