#!/usr/bin/python
#
# Copyright (C) 2006, 2007, 2008 Google Inc.
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


"""AtomService provides CRUD ops. in line with the Atom Publishing Protocol.

  AtomService: Encapsulates the ability to perform insert, update and delete
               operations with the Atom Publishing Protocol on which GData is
               based. An instance can perform query, insertion, deletion, and
               update.

  HttpRequest: Function that performs a GET, POST, PUT, or DELETE HTTP request
       to the specified end point. An AtomService object or a subclass can be
       used to specify information about the request.
"""

__author__ = 'api.jscudder (Jeffrey Scudder)'

import os
import httplib
import urllib
import re
import base64
import socket
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


URL_REGEX = re.compile('http(s)?\://([\w\.-]*)(\:(\d+))?(/.*)?')


class AtomService(object):
  """Performs Atom Publishing Protocol CRUD operations.
  
  The AtomService contains methods to perform HTTP CRUD operations. 
  """

  # Default values for members
  port = 80
  ssl = False
  # If debug is True, the HTTPConnection will display debug information
  debug = False

  def __init__(self, server=None, additional_headers=None):
    """Creates a new AtomService client.
    
    Args:
      server: string (optional) The start of a URL for the server
              to which all operations should be directed. Example: 
              'www.google.com'
      additional_headers: dict (optional) Any additional HTTP headers which
                          should be included with CRUD operations.
    """

    self.server = server
    self.additional_headers = additional_headers or {}

    self.additional_headers['User-Agent'] = 'Python Google Data Client Lib'

  def _ProcessUrl(self, url, for_proxy=False):
    """Processes a passed URL.  If the URL does not begin with https?, then
    the default value for self.server is used"""
    return ProcessUrl(self, url, for_proxy=for_proxy)

  def UseBasicAuth(self, username, password, for_proxy=False):
    """Sets an Authenticaiton: Basic HTTP header containing plaintext.
    
    The username and password are base64 encoded and added to an HTTP header
    which will be included in each request. Note that your username and 
    password are sent in plaintext.

    Args:
      username: str
      password: str
    """
    UseBasicAuth(self, username, password, for_proxy=for_proxy)

  def PrepareConnection(self, full_uri):
    """Opens a connection to the server based on the full URI.

    Examines the target URI and the proxy settings, which are set as 
    environment variables, to open a connection with the server. This 
    connection is used to make an HTTP request.

    Args:
      full_uri: str Which is the target relative (lacks protocol and host) or
      absolute URL to be opened. Example:
      'https://www.google.com/accounts/ClientLogin' or
      'base/feeds/snippets' where the server is set to www.google.com.

    Returns:
      A tuple containing the httplib.HTTPConnection and the full_uri for the
      request.
    """
    return PrepareConnection(self, full_uri)   

  # Alias the old name for the above method to preserve backwards 
  # compatibility.
  _PrepareConnection = PrepareConnection
 
  # CRUD operations
  def Get(self, uri, extra_headers=None, url_params=None, escape_params=True):
    """Query the APP server with the given URI

    The uri is the portion of the URI after the server value 
    (server example: 'www.google.com').

    Example use:
    To perform a query against Google Base, set the server to 
    'base.google.com' and set the uri to '/base/feeds/...', where ... is 
    your query. For example, to find snippets for all digital cameras uri 
    should be set to: '/base/feeds/snippets?bq=digital+camera'

    Args:
      uri: string The query in the form of a URI. Example:
           '/base/feeds/snippets?bq=digital+camera'.
      extra_headers: dicty (optional) Extra HTTP headers to be included
                     in the GET request. These headers are in addition to 
                     those stored in the client's additional_headers property.
                     The client automatically sets the Content-Type and 
                     Authorization headers.
      url_params: dict (optional) Additional URL parameters to be included
                  in the query. These are translated into query arguments
                  in the form '&dict_key=value&...'.
                  Example: {'max-results': '250'} becomes &max-results=250
      escape_params: boolean (optional) If false, the calling code has already
                     ensured that the query will form a valid URL (all
                     reserved characters have been escaped). If true, this
                     method will escape the query and any URL parameters
                     provided.

    Returns:
      httplib.HTTPResponse The server's response to the GET request.
    """
    return HttpRequest(self, 'GET', None, uri, extra_headers=extra_headers, 
        url_params=url_params, escape_params=escape_params)

  def Post(self, data, uri, extra_headers=None, url_params=None, 
           escape_params=True, content_type='application/atom+xml'):
    """Insert data into an APP server at the given URI.

    Args:
      data: string, ElementTree._Element, or something with a __str__ method 
            The XML to be sent to the uri. 
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

    Returns:
      httplib.HTTPResponse Server's response to the POST request.
    """
    return HttpRequest(self, 'POST', data, uri, extra_headers=extra_headers, 
        url_params=url_params, escape_params=escape_params, 
        content_type=content_type)

  def Put(self, data, uri, extra_headers=None, url_params=None, 
           escape_params=True, content_type='application/atom+xml'):
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
  
    Returns:
      httplib.HTTPResponse Server's response to the PUT request.
    """
    return HttpRequest(self, 'PUT', data, uri, extra_headers=extra_headers, 
        url_params=url_params, escape_params=escape_params, 
        content_type=content_type)

  def Delete(self, uri, extra_headers=None, url_params=None, 
             escape_params=True):
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
      httplib.HTTPResponse Server's response to the DELETE request.
    """
    return HttpRequest(self, 'DELETE', None, uri, extra_headers=extra_headers, 
        url_params=url_params, escape_params=escape_params)


def HttpRequest(service, operation, data, uri, extra_headers=None, 
    url_params=None, escape_params=True, content_type='application/atom+xml'):
  """Performs an HTTP call to the server, supports GET, POST, PUT, and DELETE.

  Usage example, perform and HTTP GET on http://www.google.com/:
    import atom.service
    client = atom.service.AtomService()
    http_response = client.Get('http://www.google.com/')
  or you could set the client.server to 'www.google.com' and use the 
  following:
    client.server = 'www.google.com'
    http_response = client.Get('/')

  Args:
    service: atom.AtomService object which contains some of the parameters 
        needed to make the request. The following members are used to 
        construct the HTTP call: server (str), additional_headers (dict), 
        port (int), and ssl (bool).
    operation: str The HTTP operation to be performed. This is usually one of
        'GET', 'POST', 'PUT', or 'DELETE'
    data: ElementTree, filestream, list of parts, or other object which can be 
        converted to a string. 
        Should be set to None when performing a GET or PUT.
        If data is a file-like object which can be read, this method will read
        a chunk of 100K bytes at a time and send them. 
        If the data is a list of parts to be sent, each part will be evaluated
        and sent.
    uri: The beginning of the URL to which the request should be sent. 
        Examples: '/', '/base/feeds/snippets', 
        '/m8/feeds/contacts/default/base'
    extra_headers: dict of strings. HTTP headers which should be sent
        in the request. These headers are in addition to those stored in 
        service.additional_headers.
    url_params: dict of strings. Key value pairs to be added to the URL as
        URL parameters. For example {'foo':'bar', 'test':'param'} will 
        become ?foo=bar&test=param.
    escape_params: bool default True. If true, the keys and values in 
        url_params will be URL escaped when the form is constructed 
        (Special characters converted to %XX form.)
    content_type: str The MIME type for the data being sent. Defaults to
        'application/atom+xml', this is only used if data is set.
  """
  full_uri = BuildUri(uri, url_params, escape_params)
  (connection, full_uri) = PrepareConnection(service, full_uri)

  if extra_headers is None:
    extra_headers = {}

  # Turn on debug mode if the debug member is set.
  if service.debug:
    connection.debuglevel = 1

  connection.putrequest(operation, full_uri)

  # If the list of headers does not include a Content-Length, attempt to 
  # calculate it based on the data object.
  if (data and not service.additional_headers.has_key('Content-Length') and 
      not extra_headers.has_key('Content-Length')):
    content_length = __CalculateDataLength(data)
    if content_length:
      extra_headers['Content-Length'] = content_length

  if content_type:
    extra_headers['Content-Type'] = content_type 

  # Send the HTTP headers.
  if isinstance(service.additional_headers, dict):
    for header in service.additional_headers:
      connection.putheader(header, service.additional_headers[header])
  if isinstance(extra_headers, dict):
    for header in extra_headers:
      connection.putheader(header, extra_headers[header])
  connection.endheaders()

  # If there is data, send it in the request.
  if data:
    if isinstance(data, list):
      for data_part in data:
        __SendDataPart(data_part, connection)
    else:
      __SendDataPart(data, connection)

  # Return the HTTP Response from the server.
  return connection.getresponse()


def __SendDataPart(data, connection):
  if isinstance(data, str):
    #TODO add handling for unicode.
    connection.send(data)
    return
  elif ElementTree.iselement(data):
    connection.send(ElementTree.tostring(data))
    return
  # Check to see if data is a file-like object that has a read method.
  elif hasattr(data, 'read'):
    # Read the file and send it a chunk at a time.
    while 1:
      binarydata = data.read(100000)
      if binarydata == '': break
      connection.send(binarydata)
    return
  else:
    # The data object was not a file.
    # Try to convert to a string and send the data.
    connection.send(str(data))
    return


def __CalculateDataLength(data):
  """Attempts to determine the length of the data to send. 
  
  This method will respond with a length only if the data is a string or
  and ElementTree element.

  Args:
    data: object If this is not a string or ElementTree element this funtion
        will return None.
  """
  if isinstance(data, str):
    return len(data)
  elif isinstance(data, list):
    return None
  elif ElementTree.iselement(data):
    return len(ElementTree.tostring(data))
  elif hasattr(data, 'read'):
    # If this is a file-like object, don't try to guess the length.
    return None
  else:
    return len(str(data))


def PrepareConnection(service, full_uri):
  """Opens a connection to the server based on the full URI.

  Examines the target URI and the proxy settings, which are set as
  environment variables, to open a connection with the server. This
  connection is used to make an HTTP request.

  Args:
    service: atom.AtomService or a subclass. It must have a server string which
      represents the server host to which the request should be made. It may also
      have a dictionary of additional_headers to send in the HTTP request.
    full_uri: str Which is the target relative (lacks protocol and host) or
    absolute URL to be opened. Example:
    'https://www.google.com/accounts/ClientLogin' or
    'base/feeds/snippets' where the server is set to www.google.com.

  Returns:
    A tuple containing the httplib.HTTPConnection and the full_uri for the
    request.
  """
   
  (server, port, ssl, partial_uri) = ProcessUrl(service, full_uri)
  if ssl:
    # destination is https
    proxy = os.environ.get('https_proxy')
    if proxy:
      (p_server, p_port, p_ssl, p_uri) = ProcessUrl(service, proxy, True)
      proxy_username = os.environ.get('proxy-username')
      if not proxy_username:
        proxy_username = os.environ.get('proxy_username')
      proxy_password = os.environ.get('proxy-password')
      if not proxy_password:
        proxy_password = os.environ.get('proxy_password')
      if proxy_username:
        user_auth = base64.encodestring('%s:%s' % (proxy_username,
                                                   proxy_password))
        proxy_authorization = ('Proxy-authorization: Basic %s\r\n' % (
            user_auth.strip()))
      else:
        proxy_authorization = ''
      proxy_connect = 'CONNECT %s:%s HTTP/1.0\r\n' % (server, port)
      user_agent = 'User-Agent: %s\r\n' % (
          service.additional_headers['User-Agent'])
      proxy_pieces = (proxy_connect + proxy_authorization + user_agent
                       + '\r\n')

      #now connect, very simple recv and error checking
      p_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
      p_sock.connect((p_server,p_port))
      p_sock.sendall(proxy_pieces)
      response = ''

      # Wait for the full response.
      while response.find("\r\n\r\n") == -1:
        response += p_sock.recv(8192)
       
      p_status=response.split()[1]
      if p_status!=str(200):
        raise 'Error status=',str(p_status)

      # Trivial setup for ssl socket.
      ssl = socket.ssl(p_sock, None, None)
      fake_sock = httplib.FakeSocket(p_sock, ssl)

      # Initalize httplib and replace with the proxy socket.
      connection = httplib.HTTPConnection(server)
      connection.sock=fake_sock
      full_uri = partial_uri

    else:
      connection = httplib.HTTPSConnection(server, port)
      full_uri = partial_uri

  else:
    # destination is http
    proxy = os.environ.get('http_proxy')
    if proxy:
      (p_server, p_port, p_ssl, p_uri) = ProcessUrl(service.server, proxy, True)
      proxy_username = os.environ.get('proxy-username')
      if not proxy_username:
        proxy_username = os.environ.get('proxy_username')
      proxy_password = os.environ.get('proxy-password')
      if not proxy_password:
        proxy_password = os.environ.get('proxy_password')
      if proxy_username:
        UseBasicAuth(service, proxy_username, proxy_password, True)
      connection = httplib.HTTPConnection(p_server, p_port)
      if not full_uri.startswith("http://"):
        if full_uri.startswith("/"):
          full_uri = "http://%s%s" % (service.server, full_uri)
        else:
          full_uri = "http://%s/%s" % (service.server, full_uri)
    else:
      connection = httplib.HTTPConnection(server, port)
      full_uri = partial_uri

  return (connection, full_uri)


def UseBasicAuth(service, username, password, for_proxy=False):
  """Sets an Authenticaiton: Basic HTTP header containing plaintext.
  
  The username and password are base64 encoded and added to an HTTP header
  which will be included in each request. Note that your username and 
  password are sent in plaintext. The auth header is added to the 
  additional_headers dictionary in the service object.

  Args:
    service: atom.AtomService or a subclass which has an 
        additional_headers dict as a member.
    username: str
    password: str
  """
  base_64_string = base64.encodestring('%s:%s' % (username, password))
  base_64_string = base_64_string.strip()
  if for_proxy:
    header_name = 'Proxy-Authorization'
  else:
    header_name = 'Authorization'
  service.additional_headers[header_name] = 'Basic %s' % (base_64_string,)


def ProcessUrl(service, url, for_proxy=False):
  """Processes a passed URL.  If the URL does not begin with https?, then
  the default value for server is used"""

  server = service.server
  if for_proxy:
    port = 80
    ssl = False
  else:
    port = service.port
    ssl = service.ssl
  uri = url

  m = URL_REGEX.match(url)

  if m is None:
    return (server, port, ssl, uri)
  else:
    if m.group(1) is not None:
      port = 443
      ssl = True
    if m.group(3) is None:
      server = m.group(2)
    else:
      server = m.group(2)
      port = int(m.group(4))
    if m.group(5) is not None:
      uri = m.group(5)
    else:
      uri = '/'
    return (server, port, ssl, uri)


def DictionaryToParamList(url_parameters, escape_params=True):
  """Convert a dictionary of URL arguments into a URL parameter string.

  Args:
    url_parameters: The dictionaty of key-value pairs which will be converted
                    into URL parameters. For example,
                    {'dry-run': 'true', 'foo': 'bar'}
                    will become ['dry-run=true', 'foo=bar'].

  Returns:
    A list which contains a string for each key-value pair. The strings are
    ready to be incorporated into a URL by using '&'.join([] + parameter_list)
  """
  # Choose which function to use when modifying the query and parameters.
  # Use quote_plus when escape_params is true.
  transform_op = [str, urllib.quote_plus][bool(escape_params)]
  # Create a list of tuples containing the escaped version of the
  # parameter-value pairs.
  parameter_tuples = [(transform_op(param), transform_op(value))
                     for param, value in (url_parameters or {}).items()]
  # Turn parameter-value tuples into a list of strings in the form
  # 'PARAMETER=VALUE'.

  return ['='.join(x) for x in parameter_tuples]


def BuildUri(uri, url_params=None, escape_params=True):
  """Converts a uri string and a collection of parameters into a URI.

  Args:
    uri: string
    url_params: dict (optional)
    escape_params: boolean (optional)
    uri: string The start of the desired URI. This string can alrady contain
         URL parameters. Examples: '/base/feeds/snippets', 
         '/base/feeds/snippets?bq=digital+camera'
    url_parameters: dict (optional) Additional URL parameters to be included
                    in the query. These are translated into query arguments
                    in the form '&dict_key=value&...'.
                    Example: {'max-results': '250'} becomes &max-results=250
    escape_params: boolean (optional) If false, the calling code has already
                   ensured that the query will form a valid URL (all
                   reserved characters have been escaped). If true, this
                   method will escape the query and any URL parameters
                   provided.

  Returns:
    string The URI consisting of the escaped URL parameters appended to the
    initial uri string.
  """
  # Prepare URL parameters for inclusion into the GET request.
  parameter_list = DictionaryToParamList(url_params, escape_params)

  # Append the URL parameters to the URL.
  if parameter_list:
    if uri.find('?') != -1:
      # If there are already URL parameters in the uri string, add the
      # parameters after a new & character.
      full_uri = '&'.join([uri] + parameter_list)
    else:
      # The uri string did not have any URL parameters (no ? character)
      # so put a ? between the uri and URL parameters.
      full_uri = '%s%s' % (uri, '?%s' % ('&'.join([] + parameter_list)))  
  else:
    full_uri = uri
        
  return full_uri
