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


__author__ = 'api.jscudder (Jeffrey Scudder)'


import unittest
import urllib
import gdata.auth

class AuthModuleUtilitiesTest(unittest.TestCase):

  def setUp(self):
    pass

  def testGenerateClientLoginRequestBody(self):
    body = gdata.auth.GenerateClientLoginRequestBody('jo@gmail.com', 
        'password', 'test service', 'gdata.auth test')
    expected_parameters = {'Email':r'jo%40gmail.com', 'Passwd':'password',
        'service':'test+service', 'source':'gdata.auth+test',
        'accountType':'HOSTED_OR_GOOGLE'}
    self.__matchBody(body, expected_parameters)

    body = gdata.auth.GenerateClientLoginRequestBody('jo@gmail.com', 
        'password', 'test service', 'gdata.auth test', account_type='A TEST', 
        captcha_token='12345', captcha_response='test')
    expected_parameters['accountType'] = 'A+TEST'
    expected_parameters['logintoken'] = '12345' 
    expected_parameters['logincaptcha'] = 'test'
    self.__matchBody(body, expected_parameters)
    
  def __matchBody(self, body, expected_name_value_pairs):
    parameters = body.split('&')
    for param in parameters:
      (name, value) = param.split('=')
      self.assert_(expected_name_value_pairs[name] == value)

  def testGenerateClientLoginAuthToken(self):
    http_body = ('SID=DQAAAGgA7Zg8CTN\r\n'
                 'LSID=DQAAAGsAlk8BBbG\r\n'
                 'Auth=DQAAAGgAdk3fA5N')
    self.assert_(gdata.auth.GenerateClientLoginAuthToken(http_body) ==
                 'GoogleLogin auth=DQAAAGgAdk3fA5N')


class GenerateClientLoginRequestBodyTest(unittest.TestCase):

  def testPostBodyShouldMatchShortExample(self):
    auth_body = gdata.auth.GenerateClientLoginRequestBody('johndoe@gmail.com',
        'north23AZ', 'cl', 'Gulp-CalGulp-1.05')
    self.assert_(-1 < auth_body.find('Email=johndoe%40gmail.com'))
    self.assert_(-1 < auth_body.find('Passwd=north23AZ'))
    self.assert_(-1 < auth_body.find('service=cl'))
    self.assert_(-1 < auth_body.find('source=Gulp-CalGulp-1.05'))

  def testPostBodyShouldMatchLongExample(self):
    auth_body = gdata.auth.GenerateClientLoginRequestBody('johndoe@gmail.com',
        'north23AZ', 'cl', 'Gulp-CalGulp-1.05',
        captcha_token='DQAAAGgA...dkI1', captcha_response='brinmar')
    self.assert_(-1 < auth_body.find('logintoken=DQAAAGgA...dkI1'))
    self.assert_(-1 < auth_body.find('logincaptcha=brinmar'))

  def testEquivalenceWithOldLogic(self):
    email = 'jo@gmail.com'
    password = 'password'
    account_type = 'HOSTED'
    service = 'test'
    source = 'auth test'
    old_request_body = urllib.urlencode({'Email': email,
                                         'Passwd': password,
                                         'accountType': account_type,
                                         'service': service,
                                         'source': source})
    new_request_body = gdata.auth.GenerateClientLoginRequestBody(email,
         password, service, source, account_type=account_type)
    for parameter in old_request_body.split('&'):
      self.assert_(-1 < new_request_body.find(parameter))


class GenerateAuthSubUrlTest(unittest.TestCase):

  def testDefaultParameters(self):
    url = gdata.auth.GenerateAuthSubUrl('http://example.com/xyz?x=5', 
        'http://www.google.com/test/feeds')
    self.assert_(-1 < url.find(
        r'scope=http%3A%2F%2Fwww.google.com%2Ftest%2Ffeeds'))
    self.assert_(-1 < url.find(
        r'next=http%3A%2F%2Fexample.com%2Fxyz%3Fx%3D5'))
    self.assert_(-1 < url.find('secure=0'))
    self.assert_(-1 < url.find('session=1'))

  def testAllParameters(self):
    url = gdata.auth.GenerateAuthSubUrl('http://example.com/xyz?x=5',
            'http://www.google.com/test/feeds', secure=True, session=False,
            request_url='https://example.com/auth')
    self.assert_(-1 < url.find(
        r'scope=http%3A%2F%2Fwww.google.com%2Ftest%2Ffeeds'))
    self.assert_(-1 < url.find(
        r'next=http%3A%2F%2Fexample.com%2Fxyz%3Fx%3D5'))
    self.assert_(-1 < url.find('secure=1'))
    self.assert_(-1 < url.find('session=0'))
    self.assert_(url.startswith('https://example.com/auth'))


class ExtractAuthSubTokensTest(unittest.TestCase):

  def testGetTokenFromUrl(self):
    url = 'http://www.yourwebapp.com/showcalendar.html?token=CKF50YzIH'
    self.assert_(gdata.auth.AuthSubTokenFromUrl(url) == 
        'AuthSub token=CKF50YzIH')

  def testGetTokenFromHttpResponse(self):
    response_body = ('Token=DQAA...7DCTN\r\n'
        'Expiration=20061004T123456Z')
    self.assert_(gdata.auth.AuthSubTokenFromHttpBody(response_body) == 
        'AuthSub token=DQAA...7DCTN')

    
if __name__ == '__main__':
  unittest.main()
