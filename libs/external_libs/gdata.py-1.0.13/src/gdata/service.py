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


"""GDataService provides CRUD ops. and programmatic login for GData services.

  Error: A base exception class for all exceptions in the gdata_client
         module.

  CaptchaRequired: This exception is thrown when a login attempt results in a
                   captcha challenge from the ClientLogin service. When this
                   exception is thrown, the captcha_token and captcha_url are
                   set to the values provided in the server's response.

  BadAuthentication: Raised when a login attempt is made with an incorrect
                     username or password.

  NotAuthenticated: Raised if an operation requiring authentication is called
                    before a user has authenticated.

  NonAuthSubToken: Raised if a method to modify an AuthSub token is used when
                   the user is either not authenticated or is authenticated
                   through programmatic login.

  RequestError: Raised if a CRUD request returned a non-success code. 

  UnexpectedReturnType: Raised if the response from the server was not of the
                        desired type. For example, this would be raised if the
                        server sent a feed when the client requested an entry.

  GDataService: Encapsulates user credentials needed to perform insert, update
                and delete operations with the GData API. An instance can
                perform user authentication, query, insertion, deletion, and 
                update.

  Query: Eases query URI creation by allowing URI parameters to be set as 
         dictionary attributes. For example a query with a feed of 
         '/base/feeds/snippets' and ['bq'] set to 'digital camera' will 
         produce '/base/feeds/snippets?bq=digital+camera' when .ToUri() is 
         called on it.
"""


__author__ = 'api.jscudder (Jeffrey Scudder)'


import re
import httplib
import urllib
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
import atom.service
import gdata
import atom
import gdata.auth


PROGRAMMATIC_AUTH_LABEL = 'GoogleLogin auth'
AUTHSUB_AUTH_LABEL = 'AuthSub token'
AUTH_SERVER_HOST = 'https://www.google.com'


# Module level variable specifies which module should be used by GDataService
# objects to make HttpRequests. This setting can be overridden on each 
# instance of GDataService.
http_request_handler = atom.service


class Error(Exception):
  pass


class CaptchaRequired(Error):
  pass


class BadAuthentication(Error):
  pass


class NotAuthenticated(Error):
  pass


class NonAuthSubToken(Error):
  pass


class RequestError(Error):
  pass


class UnexpectedReturnType(Error):
  pass


class GDataService(atom.service.AtomService):
  """Contains elements needed for GData login and CRUD request headers.

  Maintains additional headers (tokens for example) needed for the GData 
  services to allow a user to perform inserts, updates, and deletes.
  """

  def __init__(self, email=None, password=None, account_type='HOSTED_OR_GOOGLE',
               service=None, source=None, server=None, 
               additional_headers=None, handler=None):
    """Creates an object of type GDataService.

    Args:
      email: string (optional) The user's email address, used for
          authentication.
      password: string (optional) The user's password.
      account_type: string (optional) The type of account to use. Use
          'GOOGLE' for regular Google accounts or 'HOSTED' for Google
          Apps accounts, or 'HOSTED_OR_GOOGLE' to try finding a HOSTED
          account first and, if it doesn't exist, try finding a regular
          GOOGLE account. Default value: 'HOSTED_OR_GOOGLE'.
      service: string (optional) The desired service for which credentials
          will be obtained.
      source: string (optional) The name of the user's application.
      server: string (optional) The name of the server to which a connection
          will be opened. Default value: 'base.google.com'.
      additional_headers: dictionary (optional) Any additional headers which 
          should be included with CRUD operations.
      handler: module (optional) The module whose HttpRequest function 
          should be used when making requests to the server. The default 
          value is atom.service.
    """

    self.email = email
    self.password = password
    self.account_type = account_type
    self.service = service
    self.server = server
    self.additional_headers = additional_headers or {}
    self.handler = handler or http_request_handler
    self.__SetSource(source)
    self.__auth_token = None
    self.__captcha_token = None
    self.__captcha_url = None
    self.__gsessionid = None
 
  # Define properties for GDataService
  def _SetAuthSubToken(self, auth_token):
    """Sets the token sent in requests to an AuthSub token.

    Only use this method if you have received a token from the AuthSub 
    service. The auth_token is set automatically when ProgrammaticLogin()
    is used. See documentation for Google AuthSub here:
    http://code.google.com/apis/accounts/AuthForWebApps.html .

    Args:
      auth_token: string The token returned by the AuthSub service.
    """

    self.__auth_token = '%s=%s' % (AUTHSUB_AUTH_LABEL, auth_token)
    # The auth token is only set externally when using AuthSub authentication,
    # so set the auth_type to indicate AuthSub.

  def __SetAuthSubToken(self, auth_token):
    self._SetAuthSubToken(auth_token)

  def _GetAuthToken(self):
    """Returns the auth token used for authenticating requests.

    Returns:
      string
    """

    return self.__auth_token

  def __GetAuthToken(self):
    return self._GetAuthToken()

  auth_token = property(__GetAuthToken, __SetAuthSubToken,
      doc="""Get or set the token used for authentication.""")

  def _GetCaptchaToken(self):
    """Returns a captcha token if the most recent login attempt generated one.

    The captcha token is only set if the Programmatic Login attempt failed 
    because the Google service issued a captcha challenge.

    Returns:
      string
    """

    return self.__captcha_token

  def __GetCaptchaToken(self):
    return self._GetCaptchaToken()

  captcha_token = property(__GetCaptchaToken,
      doc="""Get the captcha token for a login request.""")

  def _GetCaptchaURL(self):
    """Returns the URL of the captcha image if a login attempt generated one.
     
    The captcha URL is only set if the Programmatic Login attempt failed
    because the Google service issued a captcha challenge.

    Returns:
      string
    """

    return self.__captcha_url

  def __GetCaptchaURL(self):
    return self._GetCaptchaURL()

  captcha_url = property(__GetCaptchaURL,
      doc="""Get the captcha URL for a login request.""")

  def GetAuthSubToken(self):
    if self.__auth_token.startswith(AUTHSUB_AUTH_LABEL):
      # Strip off the leading 'AUTHSUB_AUTH_LABEL=' and just return the
      # token value.
      return self.__auth_token[len(AUTHSUB_AUTH_LABEL)+1:]
    else:
      return None

  def SetAuthSubToken(self, token):
    self.__auth_token = '%s=%s' % (AUTHSUB_AUTH_LABEL, token)

  def GetClientLoginToken(self):
    if self.__auth_token.startswith(PROGRAMMATIC_AUTH_LABEL):
      # Strip off the leading 'PROGRAMMATIC_AUTH_LABEL=' and just return the
      # token value.
      return self.__auth_token[len(PROGRAMMATIC_AUTH_LABEL)+1:]
    else:
      return None

  def SetClientLoginToken(self, token):
    self.__auth_token = '%s=%s' % (PROGRAMMATIC_AUTH_LABEL, token)

  # Private methods to create the source property.
  def __GetSource(self):
    return self.__source

  def __SetSource(self, new_source):
    self.__source = new_source
    # Update the UserAgent header to include the new application name.
    self.additional_headers['User-Agent'] = '%s GData-Python/1.0.13' % self.__source

  source = property(__GetSource, __SetSource, 
      doc="""The source is the name of the application making the request. 
             It should be in the form company_id-app_name-app_version""")

  # Authentication operations

  def ProgrammaticLogin(self, captcha_token=None, captcha_response=None):
    """Authenticates the user and sets the GData Auth token.

    Login retreives a temporary auth token which must be used with all
    requests to GData services. The auth token is stored in the GData client
    object.

    Login is also used to respond to a captcha challenge. If the user's login
    attempt failed with a CaptchaRequired error, the user can respond by
    calling Login with the captcha token and the answer to the challenge.

    Args:
      captcha_token: string (optional) The identifier for the captcha challenge
                     which was presented to the user.
      captcha_response: string (optional) The user's answer to the captch 
                        challenge.

    Raises:
      CaptchaRequired if the login service will require a captcha response
      BadAuthentication if the login service rejected the username or password
      Error if the login service responded with a 403 different from the above
    """
    request_body = gdata.auth.GenerateClientLoginRequestBody(self.email, 
        self.password, self.service, self.source, self.account_type, 
        captcha_token, captcha_response)

    auth_response = self.handler.HttpRequest(self, 'POST', request_body, 
        AUTH_SERVER_HOST + '/accounts/ClientLogin', 
        extra_headers={'Content-Length':str(len(request_body))},
        content_type='application/x-www-form-urlencoded')
    response_body = auth_response.read()

    if auth_response.status == 200:
      self.__auth_token = gdata.auth.GenerateClientLoginAuthToken(
           response_body)
      self.__captcha_token = None
      self.__captcha_url = None

    elif auth_response.status == 403:
      # Examine each line to find the error type and the captcha token and
      # captch URL if they are present.
      captcha_parameters = gdata.auth.GetCaptchChallenge(response_body, 
          captcha_base_url='%saccounts/' % AUTH_SERVER_HOST)
      if captcha_parameters:
        self.__captcha_token = captcha_parameters['token']
        self.__captcha_url = captcha_parameters['url']
        raise CaptchaRequired, 'Captcha Required'
      elif response_body.splitlines()[0] == 'Error=BadAuthentication':
        self.__captcha_token = None
        self.__captcha_url = None
        raise BadAuthentication, 'Incorrect username or password'
      else:
        self.__captcha_token = None
        self.__captcha_url = None
        raise Error, 'Server responded with a 403 code'

  def ClientLogin(self, username, password, account_type=None, service=None,
      source=None, captcha_token=None, captcha_response=None):
    """Convenience method for authenticating using ProgrammaticLogin. 
    
    Sets values for email, password, and other optional members.

    Args:
      username:
      password:
      account_type: string (optional)
      service: string (optional)
      captcha_token: string (optional)
      captcha_response: string (optional)
    """
    self.email = username
    self.password = password

    if account_type:
      self.account_type = account_type
    if service:
      self.service = service
    if source:
      self.source = source

    self.ProgrammaticLogin(captcha_token, captcha_response)

  def GenerateAuthSubURL(self, next, scope, secure=False, session=True):
    """Generate a URL at which the user will login and be redirected back.

    Users enter their credentials on a Google login page and a token is sent
    to the URL specified in next. See documentation for AuthSub login at:
    http://code.google.com/apis/accounts/AuthForWebApps.html

    Args:
      next: string The URL user will be sent to after logging in.
      scope: string The URL of the service to be accessed.
      secure: boolean (optional) Determines whether or not the issued token
              is a secure token.
      session: boolean (optional) Determines whether or not the issued token
               can be upgraded to a session token.
    """

    # Translate True/False values for parameters into numeric values acceoted
    # by the AuthSub service.
    if secure:
      secure = 1
    else:
      secure = 0

    if session:
      session = 1
    else:
      session = 0

    request_params = urllib.urlencode({'next': next, 'scope': scope,
                                    'secure': secure, 'session': session})
    return '%s/accounts/AuthSubRequest?%s' % (AUTH_SERVER_HOST, request_params)

  def UpgradeToSessionToken(self):
    """Upgrades a single use AuthSub token to a session token.

    Raises:
      NonAuthSubToken if the user's auth token is not an AuthSub token
    """
   
    if not self.__auth_token.startswith(AUTHSUB_AUTH_LABEL):
      raise NonAuthSubToken

    response = self.handler.HttpRequest(self, 'GET', None, 
        AUTH_SERVER_HOST + '/accounts/AuthSubSessionToken', 
        extra_headers={'Authorization':self.__auth_token}, 
        content_type='application/x-www-form-urlencoded')

    response_body = response.read()
    if response.status == 200:
      for response_line in response_body.splitlines():
        if response_line.startswith('Token='):
          self.SetAuthSubToken(response_line.lstrip('Token='))

  def RevokeAuthSubToken(self):
    """Revokes an existing AuthSub token.

    Raises:
      NonAuthSubToken if the user's auth token is not an AuthSub token
    """

    if not self.__auth_token.startswith(AUTHSUB_AUTH_LABEL):
      raise NonAuthSubToken
    
    response = self.handler.HttpRequest(self, 'GET', None, 
        AUTH_SERVER_HOST + '/accounts/AuthSubRevokeToken', 
        extra_headers={'Authorization':self.__auth_token}, 
        content_type='application/x-www-form-urlencoded')
    if response.status == 200:
      self.__auth_token = None

  # CRUD operations
  def Get(self, uri, extra_headers=None, redirects_remaining=4, 
      encoding='UTF-8', converter=None):
    """Query the GData API with the given URI

    The uri is the portion of the URI after the server value 
    (ex: www.google.com).

    To perform a query against Google Base, set the server to 
    'base.google.com' and set the uri to '/base/feeds/...', where ... is 
    your query. For example, to find snippets for all digital cameras uri 
    should be set to: '/base/feeds/snippets?bq=digital+camera'

    Args:
      uri: string The query in the form of a URI. Example:
           '/base/feeds/snippets?bq=digital+camera'.
      extra_headers: dictionary (optional) Extra HTTP headers to be included
                     in the GET request. These headers are in addition to 
                     those stored in the client's additional_headers property.
                     The client automatically sets the Content-Type and 
                     Authorization headers.
      redirects_remaining: int (optional) Tracks the number of additional
          redirects this method will allow. If the service object receives
          a redirect and remaining is 0, it will not follow the redirect. 
          This was added to avoid infinite redirect loops.
      encoding: string (optional) The character encoding for the server's
          response. Default is UTF-8
      converter: func (optional) A function which will transform
          the server's results before it is returned. Example: use 
          GDataFeedFromString to parse the server response as if it
          were a GDataFeed.

    Returns:
      If there is no ResultsTransformer specified in the call, a GDataFeed 
      or GDataEntry depending on which is sent from the server. If the 
      response is niether a feed or entry and there is no ResultsTransformer,
      return a string. If there is a ResultsTransformer, the returned value 
      will be that of the ResultsTransformer function.
    """

    if extra_headers is None:
      extra_headers = {}

    # Add the authentication header to the Get request
    if self.__auth_token:
      extra_headers['Authorization'] = self.__auth_token

    if self.__gsessionid is not None:
      if uri.find('gsessionid=') < 0:
        if uri.find('?') > -1:
          uri += '&gsessionid=%s' % (self.__gsessionid,)
        else:
          uri += '?gsessionid=%s' % (self.__gsessionid,)

    server_response = self.handler.HttpRequest(self, 'GET', None, uri, 
        extra_headers=extra_headers)
    result_body = server_response.read()

    if server_response.status == 200:
      if converter:
        return converter(result_body)
      # There was no ResultsTransformer specified, so try to convert the
      # server's response into a GDataFeed.
      feed = gdata.GDataFeedFromString(result_body)
      if not feed:
        # If conversion to a GDataFeed failed, try to convert the server's
        # response to a GDataEntry.
        entry = gdata.GDataEntryFromString(result_body)
        if not entry:
          # The server's response wasn't a feed, or an entry, so return the
          # response body as a string.
          return result_body
        return entry
      return feed
    elif server_response.status == 302:
      if redirects_remaining > 0:
        location = server_response.getheader('Location')
        if location is not None:
          m = re.compile('[\?\&]gsessionid=(\w*)').search(location)
          if m is not None:
            self.__gsessionid = m.group(1)
          return self.Get(location, extra_headers, redirects_remaining - 1, 
              encoding=encoding, converter=converter)
        else:
          raise RequestError, {'status': server_response.status,
              'reason': '302 received without Location header',
              'body': result_body}
      else:
        raise RequestError, {'status': server_response.status,
            'reason': 'Redirect received, but redirects_remaining <= 0',
            'body': result_body}
    else:
      raise RequestError, {'status': server_response.status,
          'reason': server_response.reason, 'body': result_body}

  def GetMedia(self, uri, extra_headers=None):
    """Returns a MediaSource containing media and its metadata from the given
    URI string.
    """
    response_handle = self.handler.HttpRequest(self, 'GET', None, uri, 
        extra_headers=extra_headers)
    return gdata.MediaSource(response_handle, response_handle.getheader('Content-Type'),
        response_handle.getheader('Content-Length'))

  def GetEntry(self, uri, extra_headers=None):
    """Query the GData API with the given URI and receive an Entry.
    
    See also documentation for gdata.service.Get

    Args:
      uri: string The query in the form of a URI. Example:
           '/base/feeds/snippets?bq=digital+camera'.
      extra_headers: dictionary (optional) Extra HTTP headers to be included
                     in the GET request. These headers are in addition to
                     those stored in the client's additional_headers property.
                     The client automatically sets the Content-Type and
                     Authorization headers.

    Returns:
      A GDataEntry built from the XML in the server's response.
    """

    result = self.Get(uri, extra_headers, converter=atom.EntryFromString)
    if isinstance(result, atom.Entry):
      return result
    else:
      raise UnexpectedReturnType, 'Server did not send an entry' 

  def GetFeed(self, uri, extra_headers=None, 
              converter=gdata.GDataFeedFromString):
    """Query the GData API with the given URI and receive a Feed.

    See also documentation for gdata.service.Get

    Args:
      uri: string The query in the form of a URI. Example:
           '/base/feeds/snippets?bq=digital+camera'.
      extra_headers: dictionary (optional) Extra HTTP headers to be included
                     in the GET request. These headers are in addition to
                     those stored in the client's additional_headers property.
                     The client automatically sets the Content-Type and
                     Authorization headers.

    Returns:
      A GDataFeed built from the XML in the server's response.
    """

    result = self.Get(uri, extra_headers, converter=converter)
    if isinstance(result, atom.Feed):
      return result
    else:
      raise UnexpectedReturnType, 'Server did not send a feed'  

  def GetNext(self, feed):
    """Requests the next 'page' of results in the feed.
    
    This method uses the feed's next link to request an additional feed
    and uses the class of the feed to convert the results of the GET request.

    Args:
      feed: atom.Feed or a subclass. The feed should contain a next link and
          the type of the feed will be applied to the results from the 
          server. The new feed which is returned will be of the same class
          as this feed which was passed in.

    Returns:
      A new feed representing the next set of results in the server's feed.
      The type of this feed will match that of the feed argument.
    """
    next_link = feed.GetNextLink()
    # Create a closure which will convert an XML string to the class of
    # the feed object passed in.
    def ConvertToFeedClass(xml_string):
      return atom.CreateClassFromXMLString(feed.__class__, xml_string)
    # Make a GET request on the next link and use the above closure for the
    # converted which processes the XML string from the server.
    if next_link and next_link.href:
      return self.Get(next_link.href, converter=ConvertToFeedClass)
    else:
      return None

  def Post(self, data, uri, extra_headers=None, url_params=None,
           escape_params=True, redirects_remaining=4, media_source=None,
           converter=None):
    """Insert or update  data into a GData service at the given URI.

    Args:
      data: string, ElementTree._Element, atom.Entry, or gdata.GDataEntry The
            XML to be sent to the uri.
      uri: string The location (feed) to which the data should be inserted.
           Example: '/base/feeds/items'.
      extra_headers: dict (optional) HTTP headers which are to be included.
                     The client automatically sets the Content-Type,
                     Authorization, and Content-Length headers.
      url_params: dict (optional) Additional URL parameters to be included
                  in the URI. These are translated into query arguments
                  in the form '&dict_key=value&...'.
                  Example: {'max-results': '250'} becomes &max-results=250
      escape_params: boolean (optional) If false, the calling code has already
                     ensured that the query will form a valid URL (all
                     reserved characters have been escaped). If true, this
                     method will escape the query and any URL parameters
                     provided.
      media_source: MediaSource (optional) Container for the media to be sent
          along with the entry, if provided.
      converter: func (optional) A function which will be executed on the
          server's response. Often this is a function like
          GDataEntryFromString which will parse the body of the server's
          response and return a GDataEntry.

    Returns:
      If the post succeeded, this method will return a GDataFeed, GDataEntry,
      or the results of running converter on the server's result body (if
      converter was specified).
    """
    return self.PostOrPut('POST', data, uri, extra_headers=extra_headers, 
        url_params=url_params, escape_params=escape_params, 
        redirects_remaining=redirects_remaining, 
        media_source=media_source, converter=converter)

  def PostOrPut(self, verb, data, uri, extra_headers=None, url_params=None, 
           escape_params=True, redirects_remaining=4, media_source=None, 
           converter=None):
    """Insert data into a GData service at the given URI.

    Args:
      verb: string, either 'POST' or 'PUT'
      data: string, ElementTree._Element, atom.Entry, or gdata.GDataEntry The
            XML to be sent to the uri. 
      uri: string The location (feed) to which the data should be inserted. 
           Example: '/base/feeds/items'. 
      extra_headers: dict (optional) HTTP headers which are to be included. 
                     The client automatically sets the Content-Type,
                     Authorization, and Content-Length headers.
      url_params: dict (optional) Additional URL parameters to be included
                  in the URI. These are translated into query arguments
                  in the form '&dict_key=value&...'.
                  Example: {'max-results': '250'} becomes &max-results=250
      escape_params: boolean (optional) If false, the calling code has already
                     ensured that the query will form a valid URL (all
                     reserved characters have been escaped). If true, this
                     method will escape the query and any URL parameters
                     provided.
      media_source: MediaSource (optional) Container for the media to be sent
          along with the entry, if provided.
      converter: func (optional) A function which will be executed on the 
          server's response. Often this is a function like 
          GDataEntryFromString which will parse the body of the server's 
          response and return a GDataEntry.

    Returns:
      If the post succeeded, this method will return a GDataFeed, GDataEntry,
      or the results of running converter on the server's result body (if
      converter was specified).
    """
    if extra_headers is None:
      extra_headers = {}

    # Add the authentication header to the Get request
    if self.__auth_token:
      extra_headers['Authorization'] = self.__auth_token

    if self.__gsessionid is not None:
      if uri.find('gsessionid=') < 0:
        if uri.find('?') > -1:
          uri += '&gsessionid=%s' % (self.__gsessionid,)
        else:
          uri += '?gsessionid=%s' % (self.__gsessionid,)

    if data and media_source:
      if ElementTree.iselement(data):
        data_str = ElementTree.tostring(data)
      else:
        data_str = str(data)
        
      multipart = []
      multipart.append('Media multipart posting\r\n--END_OF_PART\r\n' + \
          'Content-Type: application/atom+xml\r\n\r\n')
      multipart.append('\r\n--END_OF_PART\r\nContent-Type: ' + \
          media_source.content_type+'\r\n\r\n')
      multipart.append('\r\n--END_OF_PART--\r\n')
        
      extra_headers['MIME-version'] = '1.0'
      extra_headers['Content-Length'] = str(len(multipart[0]) +
          len(multipart[1]) + len(multipart[2]) +
          len(data_str) + media_source.content_length)

      server_response = self.handler.HttpRequest(self, verb, 
          [multipart[0], data_str, multipart[1], media_source.file_handle,
              multipart[2]], uri,
          extra_headers=extra_headers, url_params=url_params, 
          escape_params=escape_params, 
          content_type='multipart/related; boundary=END_OF_PART')
      result_body = server_response.read()
      
    elif media_source or isinstance(data, gdata.MediaSource):
      if isinstance(data, gdata.MediaSource):
        media_source = data
      extra_headers['Content-Length'] = media_source.content_length
      server_response = self.handler.HttpRequest(self, verb, 
          media_source.file_handle, uri, extra_headers=extra_headers, 
          url_params=url_params, escape_params=escape_params, 
          content_type=media_source.content_type)
      result_body = server_response.read()

    else:
      http_data = data
      content_type = 'application/atom+xml'
      server_response = self.handler.HttpRequest(self, verb, 
          http_data, uri, extra_headers=extra_headers, 
          url_params=url_params, escape_params=escape_params, 
          content_type=content_type)
      result_body = server_response.read()

    # Server returns 201 for most post requests, but when performing a batch
    # request the server responds with a 200 on success.
    if server_response.status == 201 or server_response.status == 200:
      if converter:
        return converter(result_body)
      feed = gdata.GDataFeedFromString(result_body)
      if not feed:
        entry = gdata.GDataEntryFromString(result_body)
        if not entry:
          return result_body
        return entry
      return feed
    elif server_response.status == 302:
      if redirects_remaining > 0:
        location = server_response.getheader('Location')
        if location is not None:
          m = re.compile('[\?\&]gsessionid=(\w*)').search(location)
          if m is not None:
            self.__gsessionid = m.group(1) 
          return self.Post(data, location, extra_headers, url_params,
              escape_params, redirects_remaining - 1, media_source, 
              converter=converter)
        else:
          raise RequestError, {'status': server_response.status,
              'reason': '302 received without Location header',
              'body': result_body}
      else:
        raise RequestError, {'status': server_response.status,
            'reason': 'Redirect received, but redirects_remaining <= 0',
            'body': result_body}
    else:
      raise RequestError, {'status': server_response.status,
          'reason': server_response.reason, 'body': result_body}

  def Put(self, data, uri, extra_headers=None, url_params=None, 
          escape_params=True, redirects_remaining=3, media_source=None,
          converter=None):
    """Updates an entry at the given URI.
     
    Args:
      data: string, ElementTree._Element, or xml_wrapper.ElementWrapper The 
            XML containing the updated data.
      uri: string A URI indicating entry to which the update will be applied.
           Example: '/base/feeds/items/ITEM-ID'
      extra_headers: dict (optional) HTTP headers which are to be included.
                     The client automatically sets the Content-Type,
                     Authorization, and Content-Length headers.
      url_params: dict (optional) Additional URL parameters to be included
                  in the URI. These are translated into query arguments
                  in the form '&dict_key=value&...'.
                  Example: {'max-results': '250'} becomes &max-results=250
      escape_params: boolean (optional) If false, the calling code has already
                     ensured that the query will form a valid URL (all
                     reserved characters have been escaped). If true, this
                     method will escape the query and any URL parameters
                     provided.
      converter: func (optional) A function which will be executed on the 
          server's response. Often this is a function like 
          GDataEntryFromString which will parse the body of the server's 
          response and return a GDataEntry.

    Returns:
      If the put succeeded, this method will return a GDataFeed, GDataEntry,
      or the results of running converter on the server's result body (if
      converter was specified).
    """
    return self.PostOrPut('PUT', data, uri, extra_headers=extra_headers, 
        url_params=url_params, escape_params=escape_params, 
        redirects_remaining=redirects_remaining, 
        media_source=media_source, converter=converter)

  def Delete(self, uri, extra_headers=None, url_params=None, 
             escape_params=True, redirects_remaining=4):
    """Deletes the entry at the given URI.

    Args:
      uri: string The URI of the entry to be deleted. Example: 
           '/base/feeds/items/ITEM-ID'
      extra_headers: dict (optional) HTTP headers which are to be included.
                     The client automatically sets the Content-Type and
                     Authorization headers.
      url_params: dict (optional) Additional URL parameters to be included
                  in the URI. These are translated into query arguments
                  in the form '&dict_key=value&...'.
                  Example: {'max-results': '250'} becomes &max-results=250
      escape_params: boolean (optional) If false, the calling code has already
                     ensured that the query will form a valid URL (all
                     reserved characters have been escaped). If true, this
                     method will escape the query and any URL parameters
                     provided.

    Returns:
      True if the entry was deleted.
    """
    if extra_headers is None:
      extra_headers = {}

    # Add the authentication header to the Get request
    if self.__auth_token:
      extra_headers['Authorization'] = self.__auth_token

    if self.__gsessionid is not None:
      if uri.find('gsessionid=') < 0:
        if uri.find('?') > -1:
          uri += '&gsessionid=%s' % (self.__gsessionid,)
        else:
          uri += '?gsessionid=%s' % (self.__gsessionid,)
  
    server_response = self.handler.HttpRequest(self, 'DELETE', None, uri,
        extra_headers=extra_headers, url_params=url_params, 
        escape_params=escape_params)
    result_body = server_response.read()

    if server_response.status == 200:
      return True
    elif server_response.status == 302:
      if redirects_remaining > 0:
        location = server_response.getheader('Location')
        if location is not None:
          m = re.compile('[\?\&]gsessionid=(\w*)').search(location)
          if m is not None:
            self.__gsessionid = m.group(1) 
          return self.Delete(location, extra_headers, url_params,
              escape_params, redirects_remaining - 1)
        else:
          raise RequestError, {'status': server_response.status,
              'reason': '302 received without Location header',
              'body': result_body}
      else:
        raise RequestError, {'status': server_response.status,
            'reason': 'Redirect received, but redirects_remaining <= 0',
            'body': result_body}
    else:
      raise RequestError, {'status': server_response.status,
          'reason': server_response.reason, 'body': result_body}


class Query(dict):
  """Constructs a query URL to be used in GET requests
  
  Url parameters are created by adding key-value pairs to this object as a 
  dict. For example, to add &max-results=25 to the URL do
  my_query['max-results'] = 25

  Category queries are created by adding category strings to the categories
  member. All items in the categories list will be concatenated with the /
  symbol (symbolizing a category x AND y restriction). If you would like to OR
  2 categories, append them as one string with a | between the categories. 
  For example, do query.categories.append('Fritz|Laurie') to create a query
  like this feed/-/Fritz%7CLaurie . This query will look for results in both
  categories.
  """

  def __init__(self, feed=None, text_query=None, params=None, 
      categories=None):
    """Constructor for Query
    
    Args:
      feed: str (optional) The path for the feed (Examples: 
          '/base/feeds/snippets' or 'calendar/feeds/jo@gmail.com/private/full'
      text_query: str (optional) The contents of the q query parameter. The
          contents of the text_query are URL escaped upon conversion to a URI.
      params: dict (optional) Parameter value string pairs which become URL
          params when translated to a URI. These parameters are added to the
          query's items (key-value pairs).
      categories: list (optional) List of category strings which should be
          included as query categories. See 
          http://code.google.com/apis/gdata/reference.html#Queries for 
          details. If you want to get results from category A or B (both 
          categories), specify a single list item 'A|B'. 
    """
    
    self.feed = feed
    self.categories = categories or []
    if text_query:
      self.text_query = text_query
    if isinstance(params, dict):
      for param in params:
        self[param] = params[param]
    if isinstance(categories, list):
      for category in categories:
        self.categories.append(category)

  def _GetTextQuery(self):
    if 'q' in self.keys():
      return self['q']
    else:
      return None

  def _SetTextQuery(self, query):
    self['q'] = query

  text_query = property(_GetTextQuery, _SetTextQuery, 
      doc="""The feed query's q parameter""")

  def _GetAuthor(self):
    if 'author' in self.keys():
      return self['author']
    else:
      return None

  def _SetAuthor(self, query):
    self['author'] = query

  author = property(_GetAuthor, _SetAuthor,
      doc="""The feed query's author parameter""")

  def _GetAlt(self):
    if 'alt' in self.keys():
      return self['alt']
    else:
      return None

  def _SetAlt(self, query):
    self['alt'] = query

  alt = property(_GetAlt, _SetAlt,
      doc="""The feed query's alt parameter""")

  def _GetUpdatedMin(self):
    if 'updated-min' in self.keys():
      return self['updated-min']
    else:
      return None

  def _SetUpdatedMin(self, query):
    self['updated-min'] = query

  updated_min = property(_GetUpdatedMin, _SetUpdatedMin,
      doc="""The feed query's updated-min parameter""")

  def _GetUpdatedMax(self):
    if 'updated-max' in self.keys():
      return self['updated-max']
    else:
      return None

  def _SetUpdatedMax(self, query):
    self['updated-max'] = query

  updated_max = property(_GetUpdatedMax, _SetUpdatedMax,
      doc="""The feed query's updated-max parameter""")

  def _GetPublishedMin(self):
    if 'published-min' in self.keys():
      return self['published-min']
    else:
      return None

  def _SetPublishedMin(self, query):
    self['published-min'] = query

  published_min = property(_GetPublishedMin, _SetPublishedMin,
      doc="""The feed query's published-min parameter""")

  def _GetPublishedMax(self):
    if 'published-max' in self.keys():
      return self['published-max']
    else:
      return None

  def _SetPublishedMax(self, query):
    self['published-max'] = query

  published_max = property(_GetPublishedMax, _SetPublishedMax,
      doc="""The feed query's published-max parameter""")

  def _GetStartIndex(self):
    if 'start-index' in self.keys():
      return self['start-index']
    else:
      return None

  def _SetStartIndex(self, query):
    if not isinstance(query, str):
      query = str(query)
    self['start-index'] = query

  start_index = property(_GetStartIndex, _SetStartIndex,
      doc="""The feed query's start-index parameter""")

  def _GetMaxResults(self):
    if 'max-results' in self.keys():
      return self['max-results']
    else:
      return None

  def _SetMaxResults(self, query):
    if not isinstance(query, str):
      query = str(query)
    self['max-results'] = query

  max_results = property(_GetMaxResults, _SetMaxResults,
      doc="""The feed query's max-results parameter""")

  def _GetOrderBy(self):
    if 'orderby' in self.keys():
      return self['orderby']
    else:
      return None
 
  def _SetOrderBy(self, query):
    self['orderby'] = query
  
  orderby = property(_GetOrderBy, _SetOrderBy, 
      doc="""The feed query's orderby parameter""")

  def ToUri(self):
    q_feed = self.feed or ''
    category_string = '/'.join(
        [urllib.quote_plus(c) for c in self.categories])
    # Add categories to the feed if there are any.
    if len(self.categories) > 0:
      q_feed = q_feed + '/-/' + category_string
    return atom.service.BuildUri(q_feed, self)

  def __str__(self):
    return self.ToUri()
