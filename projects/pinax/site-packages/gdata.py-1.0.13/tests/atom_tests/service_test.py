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

__author__ = 'jscudder@google.com (Jeff Scudder)'

import unittest
import atom.service

class AtomServiceUnitTest(unittest.TestCase):
  
  def setUp(self):
    pass

  def tearDown(self):
    pass

  def testBuildUriWithNoParams(self):
    x = atom.service.BuildUri('/base/feeds/snippets')
    self.assert_(x == '/base/feeds/snippets')

  def testBuildUriWithParams(self):
    # Add parameters to a URI
    x = atom.service.BuildUri('/base/feeds/snippets', url_params={'foo': 'bar', 
                                                     'bq': 'digital camera'})
    self.assert_(x == '/base/feeds/snippets?foo=bar&bq=digital+camera')
    self.assert_(x.startswith('/base/feeds/snippets'))
    self.assert_(x.count('?') == 1)
    self.assert_(x.count('&') == 1)
    self.assert_(x.index('?') < x.index('&'))
    self.assert_(x.index('bq=digital+camera') != -1)

    # Add parameters to a URI that already has parameters
    x = atom.service.BuildUri('/base/feeds/snippets?bq=digital+camera', 
                             url_params={'foo': 'bar', 'max-results': '250'})
    self.assert_(x.startswith('/base/feeds/snippets?bq=digital+camera'))
    self.assert_(x.count('?') == 1)
    self.assert_(x.count('&') == 2)
    self.assert_(x.index('?') < x.index('&'))
    self.assert_(x.index('max-results=250') != -1)
    self.assert_(x.index('foo=bar') != -1)


  def testBuildUriWithoutParameterEscaping(self):
    x = atom.service.BuildUri('/base/feeds/snippets', 
            url_params={'foo': ' bar', 'bq': 'digital camera'}, 
            escape_params=False)
    self.assert_(x.index('foo= bar') != -1)
    self.assert_(x.index('bq=digital camera') != -1)

  def testParseHttpUrl(self):
    as = atom.service.AtomService('code.google.com')
    self.assertEquals(as.server, 'code.google.com')
    (host, port, ssl, path) =  as._ProcessUrl(
        'http://www.google.com/service/subservice?name=value')

    self.assertEquals(ssl, False)
    self.assertEquals(host, 'www.google.com')
    self.assertEquals(port, 80)
    self.assertEquals(path, '/service/subservice?name=value')

  def testParseHttpUrlWithPort(self):
    as = atom.service.AtomService('code.google.com')
    self.assertEquals(as.server, 'code.google.com')
    (host, port, ssl, path) =  as._ProcessUrl(
        'http://www.google.com:12/service/subservice?name=value&newname=newvalue')

    self.assertEquals(ssl, False)
    self.assertEquals(host, 'www.google.com')
    self.assertEquals(port, 12)
    self.assertEquals(path, '/service/subservice?name=value&newname=newvalue')

  def testParseHttpsUrl(self):
    as = atom.service.AtomService('code.google.com')
    self.assertEquals(as.server, 'code.google.com')
    (host, port, ssl, path) =  as._ProcessUrl(
        'https://www.google.com/service/subservice?name=value&newname=newvalue')

    self.assertEquals(ssl, True)
    self.assertEquals(host, 'www.google.com')
    self.assertEquals(port, 443)
    self.assertEquals(path, '/service/subservice?name=value&newname=newvalue')

  def testParseHttpsUrlWithPort(self):
    as = atom.service.AtomService('code.google.com')
    self.assertEquals(as.server, 'code.google.com')
    (host, port, ssl, path) =  as._ProcessUrl(
        'https://www.google.com:13981/service/subservice?name=value&newname=newvalue')

    self.assertEquals(ssl, True)
    self.assertEquals(host, 'www.google.com')
    self.assertEquals(port, 13981)
    self.assertEquals(path, '/service/subservice?name=value&newname=newvalue')

  def testSetBasicAuth(self):
    client = atom.service.AtomService()
    client.UseBasicAuth('foo', 'bar')
    self.assertEquals(client.additional_headers['Authorization'], 
        'Basic Zm9vOmJhcg==')
    client.UseBasicAuth('','')
    self.assertEquals(client.additional_headers['Authorization'],
        'Basic Og==')


if __name__ == '__main__':
  unittest.main()
