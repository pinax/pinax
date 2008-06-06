#!/usr/bin/python
#
# Copyright (C) 2008 Google Inc.
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

"""ContactsService extends the GDataService to streamline Google Contacts operations.

  ContactsService: Provides methods to query feeds and manipulate items. Extends 
                GDataService.

  DictionaryToParamList: Function which converts a dictionary into a list of 
                         URL arguments (represented as strings). This is a 
                         utility function used in CRUD operations.
"""

__author__ = 'dbrattli (Dag Brattli)'


import gdata
import atom.service
import gdata.service
import gdata.calendar
import atom

class Error(Exception):
  pass

class RequestError(Error):
  pass

class ContactsService(gdata.service.GDataService):
  """Client for the Google Contats service."""

  def __init__(self, email=None, password=None, source=None, 
               server='www.google.com', 
               additional_headers=None):
    gdata.service.GDataService.__init__(self, email=email, password=password,
                                        service='cp', source=source, 
                                        server=server, 
                                        additional_headers=additional_headers)

  def GetContactsFeed(self, 
      uri='http://www.google.com/m8/feeds/contacts/default/base'):
    return self.Get(uri, converter=gdata.contacts.ContactsFeedFromString)

  def CreateContact(self, new_contact, 
      insert_uri='/m8/feeds/contacts/default/base', url_params=None, 
      escape_params=True):
    """Adds an event to Google Contacts.

    Args: 
      new_contact: atom.Entry or subclass A new event which is to be added to
                Google Contacts.
      insert_uri: the URL to post new contacts to the feed
      url_params: dict (optional) Additional URL parameters to be included
                  in the insertion request. 
      escape_params: boolean (optional) If true, the url_parameters will be
                     escaped before they are included in the request.

    Returns:
      On successful insert,  an entry containing the contact created
      On failure, a RequestError is raised of the form:
        {'status': HTTP status code from server, 
         'reason': HTTP reason from the server, 
         'body': HTTP body of the server's response}
    """
    return self.Post(new_contact, insert_uri, url_params=url_params,
        escape_params=escape_params,
        converter=gdata.contacts.ContactEntryFromString)

      
  def UpdateContact(self, edit_uri, updated_contact, url_params=None, 
                    escape_params=True):
    """Updates an existing contact.

    Args:
      edit_uri: string The edit link URI for the element being updated
      updated_contact: string, atom.Entry or subclass containing
                    the Atom Entry which will replace the event which is 
                    stored at the edit_url 
      url_params: dict (optional) Additional URL parameters to be included
                  in the update request.
      escape_params: boolean (optional) If true, the url_parameters will be
                     escaped before they are included in the request.

    Returns:
      On successful update,  a httplib.HTTPResponse containing the server's
        response to the PUT request.
      On failure, a RequestError is raised of the form:
        {'status': HTTP status code from server, 
         'reason': HTTP reason from the server, 
         'body': HTTP body of the server's response}
    """
    url_prefix = 'http://%s/' % self.server
    if edit_uri.startswith(url_prefix):
      edit_uri = edit_uri[len(url_prefix):]
    response = self.Put(updated_contact, '/%s' % edit_uri,
                        url_params=url_params, 
                        escape_params=escape_params)
    if isinstance(response, atom.Entry):
      return gdata.contacts.ContactEntryFromString(response.ToString())
    else:
      return response

  def DeleteContact(self, edit_uri, extra_headers=None, 
      url_params=None, escape_params=True):
    """Removes an event with the specified ID from Google Contacts.

    Args:
      edit_uri: string The edit URL of the entry to be deleted. Example:
               'http://www.google.com/m8/feeds/contacts/default/base/xxx/yyy'
      url_params: dict (optional) Additional URL parameters to be included
                  in the deletion request.
      escape_params: boolean (optional) If true, the url_parameters will be
                     escaped before they are included in the request.

    Returns:
      On successful delete,  a httplib.HTTPResponse containing the server's
        response to the DELETE request.
      On failure, a RequestError is raised of the form:
        {'status': HTTP status code from server, 
         'reason': HTTP reason from the server, 
         'body': HTTP body of the server's response}
    """
    
    url_prefix = 'http://%s/' % self.server
    if edit_uri.startswith(url_prefix):
      edit_uri = edit_uri[len(url_prefix):]
    return self.Delete('/%s' % edit_uri,
                       url_params=url_params, escape_params=escape_params)


class ContactsQuery(gdata.service.Query):

  def __init__(self, feed=None, text_query=None, params=None,
      categories=None):
    self.feed = feed or '/m8/feeds/contacts/default/base'
    gdata.service.Query.__init__(self, feed=self.feed, text_query=text_query,
        params=params, categories=categories)
