#!/usr/bin/python
#
# Copyright (C) 2007 SIOS Technology, Inc.
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

__author__ = 'tmatsuo@sios.com (Takashi MATSUO)'

try:
  from xml.etree import cElementTree as ElementTree
except ImportError:
  try:
    import cElementTree as ElementTree
  except ImportError:
    try:
      from xml.etree import ElementTree
    except ImportError:
      from elementtree import ElementTree
import urllib
import gdata
import atom.service
import gdata.service
import gdata.apps
import atom

API_VER="2.0"
HTTP_OK=200

UNKOWN_ERROR=1000
USER_DELETED_RECENTLY=1100
USER_SUSPENDED=1101
DOMAIN_USER_LIMIT_EXCEEDED=1200
DOMAIN_ALIAS_LIMIT_EXCEEDED=1201
DOMAIN_SUSPENDED=1202
DOMAIN_FEATURE_UNAVAILABLE=1203
ENTITY_EXISTS=1300
ENTITY_DOES_NOT_EXIST=1301
ENTITY_NAME_IS_RESERVED=1302
ENTITY_NAME_NOT_VALID=1303
INVALID_GIVEN_NAME=1400
INVALID_FAMILY_NAME=1401
INVALID_PASSWORD=1402
INVALID_USERNAME=1403
INVALID_HASH_FUNCTION_NAME=1404
INVALID_HASH_DIGGEST_LENGTH=1405
INVALID_EMAIL_ADDRESS=1406
INVALID_QUERY_PARAMETER_VALUE=1407
TOO_MANY_RECIPIENTS_ON_EMAIL_LIST=1500

DEFAULT_QUOTA_LIMIT='2048'

class Error(Exception):
  pass

class AppsForYourDomainException(Error):

  def __init__(self, response):

    self.args = response
    try:
      self.element_tree = ElementTree.fromstring(response['body'])
      self.error_code = int(self.element_tree[0].attrib['errorCode'])
      self.reason = self.element_tree[0].attrib['reason']
      self.invalidInput = self.element_tree[0].attrib['invalidInput']
    except:
      self.error_code = UNKOWN_ERROR

class AppsService(gdata.service.GDataService):
  """Client for the Google Apps Provisioning service."""

  def __init__(self, email=None, password=None, domain=None, source=None,
               server='www.google.com', additional_headers=None):
    gdata.service.GDataService.__init__(self, email=email, password=password,
                                        service='apps', source=source,
                                        server=server,
                                        additional_headers=additional_headers)
    self.ssl = True
    self.port = 443
    self.domain = domain

  def _baseURL(self):
    return "/a/feeds/%s" % self.domain 

  def AddAllElementsFromAllPages(self, link_finder, func):
    """retrieve all pages and add all elements"""
    next = link_finder.GetNextLink()
    while next is not None:
      next_feed = func(str(self.Get(next.href)))
      for a_entry in next_feed.entry:
        link_finder.entry.append(a_entry)
      next = next_feed.GetNextLink()
    return link_finder

  def RetrievePageOfEmailLists(self, start_email_list_name=None):
    """Retrieve one page of email list"""

    uri = "%s/emailList/%s" % (self._baseURL(), API_VER)
    if start_email_list_name is not None:
      uri += "?startEmailListName=%s" % start_email_list_name
    try:
      return gdata.apps.EmailListFeedFromString(str(self.Get(uri)))
    except gdata.service.RequestError, e:
      raise AppsForYourDomainException(e.args[0])
    
  def RetrieveAllEmailLists(self):
    """Retrieve all email list of a domain."""

    ret = self.RetrievePageOfEmailLists()
    # pagination
    return self.AddAllElementsFromAllPages(
      ret, gdata.apps.EmailListFeedFromString)

  def RetrieveEmailList(self, list_name):
    """Retreive a single email list by the list's name."""

    uri = "%s/emailList/%s/%s" % (
      self._baseURL(), API_VER, list_name)
    try:
      return self.Get(uri, converter=gdata.apps.EmailListEntryFromString)
    except gdata.service.RequestError, e:
      raise AppsForYourDomainException(e.args[0])

  def RetrieveEmailLists(self, recipient):
    """Retrieve All Email List Subscriptions for an Email Address."""

    uri = "%s/emailList/%s?recipient=%s" % (
      self._baseURL(), API_VER, recipient)
    try:
      ret = gdata.apps.EmailListFeedFromString(str(self.Get(uri)))
    except gdata.service.RequestError, e:
      raise AppsForYourDomainException(e.args[0])
    
    # pagination
    return self.AddAllElementsFromAllPages(
      ret, gdata.apps.EmailListFeedFromString)

  def RemoveRecipientFromEmailList(self, recipient, list_name):
    """Remove recipient from email list."""
    
    uri = "%s/emailList/%s/%s/recipient/%s" % (
      self._baseURL(), API_VER, list_name, recipient)
    try:
      self.Delete(uri)
    except gdata.service.RequestError, e:
      raise AppsForYourDomainException(e.args[0])

  def RetrievePageOfRecipients(self, list_name, start_recipient=None):
    """Retrieve one page of recipient of an email list. """

    uri = "%s/emailList/%s/%s/recipient" % (
      self._baseURL(), API_VER, list_name)

    if start_recipient is not None:
      uri += "?startRecipient=%s" % start_recipient
    try:
      return gdata.apps.EmailListRecipientFeedFromString(str(self.Get(uri)))
    except gdata.service.RequestError, e:
      raise AppsForYourDomainException(e.args[0])

  def RetrieveAllRecipients(self, list_name):
    """Retrieve all recipient of an email list."""

    ret = self.RetrievePageOfRecipients(list_name)
    # pagination
    return self.AddAllElementsFromAllPages(
      ret, gdata.apps.EmailListRecipientFeedFromString)

  def AddRecipientToEmailList(self, recipient, list_name):
    """Add a recipient to a email list."""

    uri = "%s/emailList/%s/%s/recipient" % (
      self._baseURL(), API_VER, list_name)
    recipient_entry = gdata.apps.EmailListRecipientEntry()
    recipient_entry.who = gdata.apps.Who(email=recipient)

    try:
      return gdata.apps.EmailListRecipientEntryFromString(
        str(self.Post(recipient_entry, uri)))
    except gdata.service.RequestError, e:
      raise AppsForYourDomainException(e.args[0])

  def DeleteEmailList(self, list_name):
    """Delete a email list"""

    uri = "%s/emailList/%s/%s" % (self._baseURL(), API_VER, list_name)
    try:
      self.Delete(uri)
    except gdata.service.RequestError, e:
      raise AppsForYourDomainException(e.args[0])

  def CreateEmailList(self, list_name):
    """Create a email list. """

    uri = "%s/emailList/%s" % (self._baseURL(), API_VER)
    email_list_entry = gdata.apps.EmailListEntry()
    email_list_entry.email_list = gdata.apps.EmailList(name=list_name)

    try: 
      return gdata.apps.EmailListEntryFromString(
        str(self.Post(email_list_entry, uri)))
    except gdata.service.RequestError, e:
      raise AppsForYourDomainException(e.args[0])

  def DeleteNickname(self, nickname):
    """Delete a nickname"""

    uri = "%s/nickname/%s/%s" % (self._baseURL(), API_VER, nickname)
    try:
      self.Delete(uri)
    except gdata.service.RequestError, e:
      raise AppsForYourDomainException(e.args[0])

  def RetrievePageOfNicknames(self, start_nickname=None):
    """Retrieve one page of nicknames in the domain"""

    uri = "%s/nickname/%s" % (self._baseURL(), API_VER)
    if start_nickname is not None:
      uri += "?startNickname=%s" % start_nickname
    try:
      return gdata.apps.NicknameFeedFromString(str(self.Get(uri)))
    except gdata.service.RequestError, e:
      raise AppsForYourDomainException(e.args[0])

  def RetrieveAllNicknames(self):
    """Retrieve all nicknames in the domain"""

    ret = self.RetrievePageOfNicknames()
    # pagination
    return self.AddAllElementsFromAllPages(
      ret, gdata.apps.NicknameFeedFromString)

  def RetrieveNicknames(self, user_name):
    """Retrieve nicknames of the user"""

    uri = "%s/nickname/%s?username=%s" % (self._baseURL(), API_VER, user_name)
    try:
      ret = gdata.apps.NicknameFeedFromString(str(self.Get(uri)))
    except gdata.service.RequestError, e:
      raise AppsForYourDomainException(e.args[0])

    # pagination
    return self.AddAllElementsFromAllPages(
      ret, gdata.apps.NicknameFeedFromString)

  def RetrieveNickname(self, nickname):
    """Retrieve a nickname.

    Args:
      nickname: string The nickname to retrieve

    Returns:
      gdata.apps.NicknameEntry
    """

    uri = "%s/nickname/%s/%s" % (self._baseURL(), API_VER, nickname)
    try:
      return gdata.apps.NicknameEntryFromString(str(self.Get(uri)))
    except gdata.service.RequestError, e:
      raise AppsForYourDomainException(e.args[0])

  def CreateNickname(self, user_name, nickname):
    """Create a nickname"""

    uri = "%s/nickname/%s" % (self._baseURL(), API_VER)
    nickname_entry = gdata.apps.NicknameEntry()
    nickname_entry.login = gdata.apps.Login(user_name=user_name)
    nickname_entry.nickname = gdata.apps.Nickname(name=nickname)

    try: 
      return gdata.apps.NicknameEntryFromString(
        str(self.Post(nickname_entry, uri)))
    except gdata.service.RequestError, e:
      raise AppsForYourDomainException(e.args[0])

  def DeleteUser(self, user_name):
    """Delete a user account"""

    uri = "%s/user/%s/%s" % (self._baseURL(), API_VER, user_name)
    try:
      return self.Delete(uri)
    except gdata.service.RequestError, e:
      raise AppsForYourDomainException(e.args[0])

  def UpdateUser(self, user_name, user_entry):
    """Update a user account."""

    uri = "%s/user/%s/%s" % (self._baseURL(), API_VER, user_name)
    try: 
      return gdata.apps.UserEntryFromString(str(self.Put(user_entry, uri)))
    except gdata.service.RequestError, e:
      raise AppsForYourDomainException(e.args[0])

  def CreateUser(self, user_name, family_name, given_name, password,
                 suspended='false', quota_limit=None, 
                 password_hash_function=None):
    """Create a user account. """

    uri = "%s/user/%s" % (self._baseURL(), API_VER)
    user_entry = gdata.apps.UserEntry()
    user_entry.login = gdata.apps.Login(
        user_name=user_name, password=password, suspended=suspended,
        hash_function_name=password_hash_function)
    user_entry.name = gdata.apps.Name(family_name=family_name,
                                      given_name=given_name)
    if quota_limit is not None:
      user_entry.quota = gdata.apps.Quota(limit=str(quota_limit))

    try: 
      return gdata.apps.UserEntryFromString(str(self.Post(user_entry, uri)))
    except gdata.service.RequestError, e:
      raise AppsForYourDomainException(e.args[0])

  def SuspendUser(self, user_name):
    user_entry = self.RetrieveUser(user_name)
    if user_entry.login.suspended != 'true':
      user_entry.login.suspended = 'true'
      user_entry = self.UpdateUser(user_name, user_entry)
    return user_entry

  def RestoreUser(self, user_name):
    user_entry = self.RetrieveUser(user_name)
    if user_entry.login.suspended != 'false':
      user_entry.login.suspended = 'false'
      user_entry = self.UpdateUser(user_name, user_entry)
    return user_entry

  def RetrieveUser(self, user_name):
    """Retrieve an user account.

    Args:
      user_name: string The user name to retrieve

    Returns:
      gdata.apps.UserEntry
    """

    uri = "%s/user/%s/%s" % (self._baseURL(), API_VER, user_name)
    try:
      return gdata.apps.UserEntryFromString(str(self.Get(uri)))
    except gdata.service.RequestError, e:
      raise AppsForYourDomainException(e.args[0])

  def RetrievePageOfUsers(self, start_username=None):
    """Retrieve one page of users in this domain."""

    uri = "%s/user/%s" % (self._baseURL(), API_VER)
    if start_username is not None:
      uri += "?startUsername=%s" % start_username
    try:
      return gdata.apps.UserFeedFromString(str(self.Get(uri)))
    except gdata.service.RequestError, e:
      raise AppsForYourDomainException(e.args[0])

  def RetrieveAllUsers(self):
    """Retrieve all users in this domain."""

    ret = self.RetrievePageOfUsers()
    # pagination
    return self.AddAllElementsFromAllPages(
      ret, gdata.apps.UserFeedFromString)
